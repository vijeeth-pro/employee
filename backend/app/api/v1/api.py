from fastapi import APIRouter
from app.api.v1 import auth, users, companies, employees, vendor_companies, vendor_employees, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users & RBAC"])
api_router.include_router(companies.router, prefix="/companies", tags=["Companies"])
api_router.include_router(employees.router, prefix="/employees", tags=["Company Employees"])
api_router.include_router(vendor_companies.router, prefix="/vendor-companies", tags=["Vendor Companies"])
api_router.include_router(vendor_employees.router, prefix="/vendor-employees", tags=["Vendor Employees"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & System"])
