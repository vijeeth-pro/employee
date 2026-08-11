from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.company import company_vendor_association

class VendorCompany(Base):
    __tablename__ = "vendor_companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)
    service_type = Column(String(100), default="IT Staffing & Consulting")
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    users = relationship("User", back_populates="vendor_company", cascade="all, delete-orphan")
    companies = relationship(
        "Company",
        secondary=company_vendor_association,
        back_populates="vendors"
    )
    policies = relationship("CompanyPolicy", back_populates="vendor_company", cascade="all, delete-orphan")
