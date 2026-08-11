# Import all models so SQLAlchemy Base metadata registers them
from app.core.database import Base
from app.models.company import Company, company_vendor_association
from app.models.vendor import VendorCompany
from app.models.user import User
from app.models.policy import CompanyPolicy
from app.models.enums import UserRole

__all__ = [
    "Base",
    "Company",
    "VendorCompany",
    "User",
    "CompanyPolicy",
    "UserRole",
    "company_vendor_association",
]
