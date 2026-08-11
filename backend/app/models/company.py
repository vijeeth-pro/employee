from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base

# Association table between Company and VendorCompany
company_vendor_association = Table(
    'company_vendor_relation',
    Base.metadata,
    Column('company_id', Integer, ForeignKey('companies.id', ondelete='CASCADE'), primary_key=True),
    Column('vendor_company_id', Integer, ForeignKey('vendor_companies.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime, default=lambda: datetime.now(timezone.utc))
)

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)
    industry = Column(String(100), default="Technology")
    status = Column(String(20), default="active") # active, inactive
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    vendors = relationship(
        "VendorCompany",
        secondary=company_vendor_association,
        back_populates="companies"
    )
    policies = relationship("CompanyPolicy", back_populates="company", cascade="all, delete-orphan")
