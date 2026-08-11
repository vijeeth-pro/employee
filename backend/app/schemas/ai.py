from typing import Optional, List
from pydantic import BaseModel

class AIChatRequest(BaseModel):
    prompt: str
    chat_history: Optional[List[dict]] = None

class AISourceDocument(BaseModel):
    title: str
    category: str
    source_type: str # policy, employee, company, vendor

class AIChatResponse(BaseModel):
    answer: str
    sources: List[AISourceDocument]
    role_applied: str
