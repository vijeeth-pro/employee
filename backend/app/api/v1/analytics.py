from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models import User, Company, VendorCompany, UserRole, company_vendor_association
from app.schemas import DashboardStats, UserOut
from app.db.init_db import init_db

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve high-level dashboard analytics filtered by current user role."""
    user_role = current_user.role

    if user_role == UserRole.ADMIN:
        total_companies = db.query(Company).count()
        total_employees = db.query(User).filter(User.role == UserRole.EMPLOYEE).count()
        total_vendors = db.query(VendorCompany).count()
        total_vendor_employees = db.query(User).filter(User.role == UserRole.VENDOR_EMPLOYEE).count()
        active_contracts = db.query(company_vendor_association).count()
        recent_users_raw = db.query(User).order_by(User.created_at.desc()).limit(5).all()

    elif user_role == UserRole.COMPANY and current_user.company_id:
        company_id = current_user.company_id
        total_companies = 1
        total_employees = db.query(User).filter(User.company_id == company_id, User.role == UserRole.EMPLOYEE).count()
        
        company = db.query(Company).filter(Company.id == company_id).first()
        assigned_vendors = company.vendors if company else []
        total_vendors = len(assigned_vendors)
        
        vendor_ids = [v.id for v in assigned_vendors]
        total_vendor_employees = db.query(User).filter(
            User.role == UserRole.VENDOR_EMPLOYEE,
            User.vendor_company_id.in_(vendor_ids)
        ).count() if vendor_ids else 0

        active_contracts = total_vendors
        recent_users_raw = db.query(User).filter(
            (User.company_id == company_id) | (User.vendor_company_id.in_(vendor_ids))
        ).order_by(User.created_at.desc()).limit(5).all() if vendor_ids else db.query(User).filter(User.company_id == company_id).limit(5).all()

    elif user_role == UserRole.VENDOR_COMPANY and current_user.vendor_company_id:
        v_id = current_user.vendor_company_id
        vendor = db.query(VendorCompany).filter(VendorCompany.id == v_id).first()
        assigned_companies = vendor.companies if vendor else []
        
        total_companies = len(assigned_companies)
        total_employees = 0
        total_vendors = 1
        total_vendor_employees = db.query(User).filter(User.vendor_company_id == v_id, User.role == UserRole.VENDOR_EMPLOYEE).count()
        active_contracts = total_companies
        recent_users_raw = db.query(User).filter(User.vendor_company_id == v_id).order_by(User.created_at.desc()).limit(5).all()

    else: # EMPLOYEE / VENDOR_EMPLOYEE
        total_companies = 1
        total_employees = 1
        total_vendors = 0
        total_vendor_employees = 0
        active_contracts = 1
        recent_users_raw = [current_user]

    recent_users = [
        UserOut(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            company_id=u.company_id,
            vendor_company_id=u.vendor_company_id,
            phone=u.phone,
            designation=u.designation,
            department=u.department,
            status=u.status,
            created_at=u.created_at,
            company_name=u.company.name if u.company else None,
            vendor_company_name=u.vendor_company.name if u.vendor_company else None
        )
        for u in recent_users_raw
    ]

    return DashboardStats(
        total_companies=total_companies,
        total_employees=total_employees,
        total_vendors=total_vendors,
        total_vendor_employees=total_vendor_employees,
        active_contracts=active_contracts,
        recent_users=recent_users
    )

@router.post("/reset-seed")
def reset_database_seed(current_user: User = Depends(require_role([UserRole.ADMIN]))):
    """Re-seed sample database records (Admin only)."""
    init_db()
    return {"message": "Database successfully re-seeded!"}
