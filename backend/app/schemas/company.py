from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class CompanyBase(BaseModel):
    name: str
    code: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = "Technology"
    status: Optional[str] = "active"

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    status: Optional[str] = None

class CompanyOut(CompanyBase):
    id: int
    created_at: datetime
    employee_count: Optional[int] = 0
    vendor_count: Optional[int] = 0

    class Config:
        from_attributes = True
