from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User, CompanyPolicy, UserRole
from app.schemas import AIChatRequest, AIChatResponse, CompanyPolicyOut
from app.services.ai_service import rag_engine

router = APIRouter()

@router.post("/chat", response_model=AIChatResponse)
def ai_chat(
    chat_data: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI RAG Chat Endpoint: Role-Aware Retrieval Augmented Generation."""
    if not chat_data.prompt.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt cannot be empty")
    
    response = rag_engine.query(chat_data.prompt, current_user, db)
    return response

@router.post("/reindex")
def reindex_vector_store(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin trigger to refresh RAG vector index."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can trigger vector reindexing")
    
    rag_engine.index_database(db)
    return {"status": "success", "message": f"Successfully re-indexed {len(rag_engine.vector_chunks)} vector documents"}

@router.get("/policies", response_model=List[CompanyPolicyOut])
def get_policies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve policies accessible to current user."""
    query = db.query(CompanyPolicy)
    if current_user.role == UserRole.ADMIN:
        return query.all()
    elif current_user.company_id:
        return query.filter(CompanyPolicy.company_id == current_user.company_id).all()
    elif current_user.vendor_company_id:
        return query.filter(CompanyPolicy.vendor_company_id == current_user.vendor_company_id).all()
    return []
