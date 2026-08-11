from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.deps import get_current_user, require_role
from app.models import User, UserRole, Company, VendorCompany
from app.schemas import UserOut, UserCreate, UserUpdate

router = APIRouter()

@router.get("/", response_model=List[UserOut])
def list_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List users filtered by role hierarchy."""
    query = db.query(User)

    # RBAC Filtering logic
    if current_user.role == UserRole.ADMIN:
        pass # Admin sees all users
    elif current_user.role == UserRole.COMPANY:
        # Company sees users from its own company AND assigned vendors
        query = query.filter(
            (User.company_id == current_user.company_id) |
            (User.vendor_company_id.in_(
                db.query(VendorCompany.id).filter(VendorCompany.companies.any(id=current_user.company_id))
            ))
        )
    elif current_user.role == UserRole.VENDOR_COMPANY:
        # Vendor Company sees its own vendor employees
        query = query.filter(User.vendor_company_id == current_user.vendor_company_id)
    else:
        # Employees/Contractors only see themselves
        query = query.filter(User.id == current_user.id)

    if role:
        query = query.filter(User.role == role)

    users = query.offset(skip).limit(limit).all()
    
    result = []
    for u in users:
        result.append(UserOut(
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
        ))
    return result

@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single user profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Permission Check
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        if current_user.role == UserRole.COMPANY and user.company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this user profile")
        if current_user.role == UserRole.VENDOR_COMPANY and user.vendor_company_id != current_user.vendor_company_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this user profile")

    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        company_id=user.company_id,
        vendor_company_id=user.vendor_company_id,
        phone=user.phone,
        designation=user.designation,
        department=user.department,
        status=user.status,
        created_at=user.created_at,
        company_name=user.company.name if user.company else None,
        vendor_company_name=user.vendor_company.name if user.vendor_company else None
    )

@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user information."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Only Admin or Company Admin can update roles/assignments
    if current_user.role not in [UserRole.ADMIN, UserRole.COMPANY, UserRole.VENDOR_COMPANY] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        company_id=user.company_id,
        vendor_company_id=user.vendor_company_id,
        phone=user.phone,
        designation=user.designation,
        department=user.department,
        status=user.status,
        created_at=user.created_at,
        company_name=user.company.name if user.company else None,
        vendor_company_name=user.vendor_company.name if user.vendor_company else None
    )

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.COMPANY, UserRole.VENDOR_COMPANY])),
    db: Session = Depends(get_db)
):
    """Delete a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.role == UserRole.COMPANY and user.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Cannot delete employee outside your company")
    if current_user.role == UserRole.VENDOR_COMPANY and user.vendor_company_id != current_user.vendor_company_id:
        raise HTTPException(status_code=403, detail="Cannot delete vendor employee outside your agency")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
