from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class VendorCompanyBase(BaseModel):
    name: str
    code: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    service_type: Optional[str] = "IT Staffing & Consulting"
    status: Optional[str] = "active"

class VendorCompanyCreate(VendorCompanyBase):
    pass

class VendorCompanyUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    service_type: Optional[str] = None
    status: Optional[str] = None

class VendorCompanyOut(VendorCompanyBase):
    id: int
    created_at: datetime
    employee_count: Optional[int] = 0

    class Config:
        from_attributes = True
