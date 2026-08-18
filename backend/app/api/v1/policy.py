import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User, CompanyPolicy
from app.schemas.policy import CompanyPolicyOut
from app.services.rag_service import (
    extract_text_from_file, chunk_text, upsert_chunks_to_vector_db
)

router = APIRouter()

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "policies")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=CompanyPolicyOut)
async def upload_policy_document(
    title: str = Form(...),
    category: str = Form("General Policy"),
    company_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload corporate policy document (PDF/TXT), extract text, 
    generate Gemini vector embeddings, and store in Pinecone DB.
    """
    # Permission check: Only Admin or Company Admin can upload policies
    if current_user.role not in ("admin", "company", "vendor.company"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: Only company or system administrators can upload policies."
        )

    # Resolve company scope
    target_company_id = company_id
    if current_user.role == "company":
        target_company_id = current_user.company_id
    
    target_vendor_company_id = None
    if current_user.role == "vendor.company":
        target_vendor_company_id = current_user.vendor_company_id

    # Save file to disk
    file_bytes = await file.read()
    file_size = len(file_bytes)
    
    safe_filename = f"{current_user.id}_{int(os.times().elapsed)}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Extract text and chunk
    try:
        raw_text = extract_text_from_file(file_bytes, file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading document: {str(e)}"
        )

    chunks = chunk_text(raw_text)
    chunk_count = len(chunks)

    # Create Database Record
    policy = CompanyPolicy(
        title=title,
        category=category,
        content=raw_text[:2000],  # Store preview content
        file_name=file.filename,
        file_path=file_path,
        file_size=file_size,
        chunk_count=chunk_count,
        company_id=target_company_id,
        vendor_company_id=target_vendor_company_id
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)

    # Embed and Upsert to Pinecone Vector DB
    try:
        upsert_chunks_to_vector_db(
            doc_id=policy.id,
            title=title,
            chunks=chunks,
            company_id=target_company_id,
            vendor_company_id=target_vendor_company_id,
            category=category
        )
    except Exception as e:
        print(f"Vector DB upsert warning: {e}")

    return policy

@router.get("/", response_model=List[CompanyPolicyOut])
def list_company_policies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List uploaded policies accessible to current user's organization."""
    query = db.query(CompanyPolicy)

    if current_user.role == "admin":
        return query.order_by(CompanyPolicy.created_at.desc()).all()
    elif current_user.company_id:
        query = query.filter((CompanyPolicy.company_id == current_user.company_id) | (CompanyPolicy.company_id.is_(None)))
    elif current_user.vendor_company_id:
        query = query.filter((CompanyPolicy.vendor_company_id == current_user.vendor_company_id) | (CompanyPolicy.vendor_company_id.is_(None)))

    return query.order_by(CompanyPolicy.created_at.desc()).all()

@router.delete("/{policy_id}")
def delete_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete policy document."""
    if current_user.role not in ("admin", "company", "vendor.company"):
        raise HTTPException(status_code=403, detail="Permission denied")

    policy = db.query(CompanyPolicy).filter(CompanyPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    if current_user.role == "company" and policy.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Cannot delete other company policy")

    db.delete(policy)
    db.commit()
    return {"message": "Policy deleted successfully"}
