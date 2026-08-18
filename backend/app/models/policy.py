from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class CompanyPolicy(Base):
    __tablename__ = "company_policies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    category = Column(String(100), default="General Policy") # Leave, Remote Work, Ethics, Conduct, Expenses
    content = Column(Text, nullable=False)
    
    file_name = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    chunk_count = Column(Integer, default=0)

    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=True)
    vendor_company_id = Column(Integer, ForeignKey("vendor_companies.id", ondelete="CASCADE"), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    company = relationship("Company", back_populates="policies")
    vendor_company = relationship("VendorCompany", back_populates="policies")

