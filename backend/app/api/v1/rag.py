from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.policy import ChatQueryRequest, ChatQueryResponse, SourceChunk
from app.services.rag_service import query_relevant_chunks, generate_rag_answer

router = APIRouter()

@router.post("/chat", response_model=ChatQueryResponse)
def rag_chat_assistant(
    request: ChatQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    RAG AI Assistant Query Endpoint:
    1. Scope vector query by user's company_id / vendor_company_id.
    2. Retrieve policy document chunks from Pinecone.
    3. Construct prompt with user profile + policy chunks.
    4. Generate response via Gemini LLM.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message query string cannot be empty."
        )

    # Calculate live leave stats
    annual_quota = getattr(current_user, "annual_leave_quota", 20) or 20
    annual_taken = getattr(current_user, "annual_leave_taken", 0) or 0
    remaining_annual = max(0, annual_quota - annual_taken)

    sick_quota = getattr(current_user, "sick_leave_quota", 10) or 10
    sick_taken = getattr(current_user, "sick_leave_taken", 0) or 0
    remaining_sick = max(0, sick_quota - sick_taken)

    user_info = {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role,
        "designation": current_user.designation,
        "department": current_user.department,
        "company_name": current_user.company.name if current_user.company else None,
        "vendor_company_name": current_user.vendor_company.name if current_user.vendor_company else None,
        # Live Database Leave Ledger Metrics
        "annual_leave_quota": annual_quota,
        "annual_leave_taken": annual_taken,
        "remaining_annual_leave": remaining_annual,
        "sick_leave_quota": sick_quota,
        "sick_leave_taken": sick_taken,
        "remaining_sick_leave": remaining_sick,
        "last_leave_date": getattr(current_user, "last_leave_date", "None") or "None",
        "last_leave_type": getattr(current_user, "last_leave_type", "None") or "None"
    }

    # Query Pinecone / Vector DB
    context_chunks = query_relevant_chunks(
        query_text=request.message,
        company_id=current_user.company_id,
        vendor_company_id=current_user.vendor_company_id,
        top_k=4
    )

    # Generate answer with Gemini LLM
    answer = generate_rag_answer(
        query_text=request.message,
        context_chunks=context_chunks,
        user_info=user_info
    )

    sources = [
        SourceChunk(
            title=c["title"],
            source_type=c["category"],
            chunk_text=c["chunk_text"][:160] + "...",
            score=c["score"]
        )
        for c in context_chunks
    ]

    return ChatQueryResponse(
        answer=answer,
        sources=sources,
        user_context={
            "role": current_user.role,
            "organization": user_info["company_name"] or user_info["vendor_company_name"] or "System Admin"
        }
    )
