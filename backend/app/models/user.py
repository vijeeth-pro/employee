from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]), nullable=False, default=UserRole.EMPLOYEE)
    
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)
    vendor_company_id = Column(Integer, ForeignKey("vendor_companies.id", ondelete="SET NULL"), nullable=True)
    
    phone = Column(String(50), nullable=True)
    designation = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    status = Column(String(20), default="active") # active, inactive
    
    # Employee Live Leave Ledger Metrics
    annual_leave_quota = Column(Integer, default=20)
    sick_leave_quota = Column(Integer, default=10)
    annual_leave_taken = Column(Integer, default=3)
    sick_leave_taken = Column(Integer, default=1)
    last_leave_date = Column(String(50), nullable=True, default="2026-08-14")
    last_leave_type = Column(String(50), nullable=True, default="Privilege Leave")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    company = relationship("Company", back_populates="users")
    vendor_company = relationship("VendorCompany", back_populates="users")
