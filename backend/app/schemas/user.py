from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.enums import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    company_id: Optional[int] = None
    vendor_company_id: Optional[int] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = "active"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    company_id: Optional[int] = None
    vendor_company_id: Optional[int] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None
    password: Optional[str] = None

class UserOut(UserBase):
    id: int
    created_at: datetime
    company_name: Optional[str] = None
    vendor_company_name: Optional[str] = None

    class Config:
        from_attributes = True
