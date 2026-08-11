from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.deps import get_current_user, require_role
from app.models import User, UserRole, VendorCompany
from app.schemas import UserOut, UserCreate

router = APIRouter()

@router.get("/", response_model=List[UserOut])
def list_vendor_employees(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List vendor employees / contractors."""
    query = db.query(User).filter(User.role == UserRole.VENDOR_EMPLOYEE)

    if current_user.role == UserRole.ADMIN:
        vendor_emps = query.all()
    elif current_user.role == UserRole.VENDOR_COMPANY and current_user.vendor_company_id:
        vendor_emps = query.filter(User.vendor_company_id == current_user.vendor_company_id).all()
    elif current_user.role == UserRole.COMPANY and current_user.company_id:
        # Show contractors from vendors assigned to this company
        vendor_ids = [v.id for v in current_user.company.vendors]
        vendor_emps = query.filter(User.vendor_company_id.in_(vendor_ids)).all()
    else:
        vendor_emps = query.filter(User.id == current_user.id).all()

    return [
        UserOut(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            company_id=None,
            vendor_company_id=u.vendor_company_id,
            phone=u.phone,
            designation=u.designation,
            department=u.department,
            status=u.status,
            created_at=u.created_at,
            company_name=None,
            vendor_company_name=u.vendor_company.name if u.vendor_company else None
        )
        for u in vendor_emps
    ]

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_vendor_employee(
    user_in: UserCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.VENDOR_COMPANY])),
    db: Session = Depends(get_db)
):
    """Register new contractor for vendor company."""
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    target_vendor_id = user_in.vendor_company_id
    if current_user.role == UserRole.VENDOR_COMPANY:
        target_vendor_id = current_user.vendor_company_id

    if not target_vendor_id:
        raise HTTPException(status_code=400, detail="Must specify valid vendor_company_id")

    vendor = db.query(VendorCompany).filter(VendorCompany.id == target_vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor company not found")

    v_emp = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=UserRole.VENDOR_EMPLOYEE,
        vendor_company_id=target_vendor_id,
        phone=user_in.phone,
        designation=user_in.designation,
        department=user_in.department,
        status=user_in.status or "active"
    )

    db.add(v_emp)
    db.commit()
    db.refresh(v_emp)

    return UserOut(
        id=v_emp.id,
        email=v_emp.email,
        full_name=v_emp.full_name,
        role=v_emp.role,
        company_id=None,
        vendor_company_id=v_emp.vendor_company_id,
        phone=v_emp.phone,
        designation=v_emp.designation,
        department=v_emp.department,
        status=v_emp.status,
        created_at=v_emp.created_at,
        company_name=None,
        vendor_company_name=vendor.name
    )
