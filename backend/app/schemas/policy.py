from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class CompanyPolicyBase(BaseModel):
    title: str
    category: Optional[str] = "General Policy"
    content: str
    company_id: Optional[int] = None
    vendor_company_id: Optional[int] = None

class CompanyPolicyCreate(CompanyPolicyBase):
    pass

class CompanyPolicyOut(CompanyPolicyBase):
    id: int
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    chunk_count: Optional[int] = 0
    created_at: datetime

    class Config:
        from_attributes = True

class SourceChunk(BaseModel):
    title: str
    source_type: str
    chunk_text: str
    score: float

class ChatQueryRequest(BaseModel):
    message: str

class ChatQueryResponse(BaseModel):
    answer: str
    sources: List[SourceChunk] = []
    user_context: Optional[dict] = None

