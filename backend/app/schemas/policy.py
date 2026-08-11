from datetime import datetime
from typing import Optional
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
    created_at: datetime

    class Config:
        from_attributes = True
