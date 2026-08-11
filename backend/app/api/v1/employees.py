from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.deps import get_current_user, require_role
from app.models import User, UserRole, Company
from app.schemas import UserOut, UserCreate

router = APIRouter()

@router.get("/", response_model=List[UserOut])
def list_company_employees(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List company employees (Role: EMPLOYEE or COMPANY Admin)."""
    query = db.query(User).filter(User.role.in_([UserRole.EMPLOYEE, UserRole.COMPANY]))
    
    if current_user.role == UserRole.ADMIN:
        employees = query.all()
    elif current_user.company_id:
        employees = query.filter(User.company_id == current_user.company_id).all()
    else:
        employees = []

    return [
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
            vendor_company_name=None
        )
        for u in employees
    ]

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_company_employee(
    user_in: UserCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.COMPANY])),
    db: Session = Depends(get_db)
):
    """Add new employee to company."""
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    target_company_id = user_in.company_id
    if current_user.role == UserRole.COMPANY:
        target_company_id = current_user.company_id

    if not target_company_id:
        raise HTTPException(status_code=400, detail="Must specify valid company_id")

    company = db.query(Company).filter(Company.id == target_company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    employee = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=UserRole.EMPLOYEE,
        company_id=target_company_id,
        phone=user_in.phone,
        designation=user_in.designation,
        department=user_in.department,
        status=user_in.status or "active"
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return UserOut(
        id=employee.id,
        email=employee.email,
        full_name=employee.full_name,
        role=employee.role,
        company_id=employee.company_id,
        vendor_company_id=None,
        phone=employee.phone,
        designation=employee.designation,
        department=employee.department,
        status=employee.status,
        created_at=employee.created_at,
        company_name=company.name,
        vendor_company_name=None
    )
