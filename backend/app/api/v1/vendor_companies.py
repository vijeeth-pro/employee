from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models import VendorCompany, Company, User, UserRole
from app.schemas import VendorCompanyOut, VendorCompanyCreate, VendorCompanyUpdate

router = APIRouter()

@router.get("/", response_model=List[VendorCompanyOut])
def list_vendor_companies(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List vendor companies accessible to current user."""
    query = db.query(VendorCompany)

    if current_user.role == UserRole.ADMIN:
        vendors = query.offset(skip).limit(limit).all()
    elif current_user.role == UserRole.COMPANY and current_user.company_id:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        vendors = company.vendors if company else []
    elif current_user.role == UserRole.VENDOR_COMPANY and current_user.vendor_company_id:
        vendors = query.filter(VendorCompany.id == current_user.vendor_company_id).all()
    else:
        vendors = query.all()

    return [
        VendorCompanyOut(
            id=v.id,
            name=v.name,
            code=v.code,
            email=v.email,
            phone=v.phone,
            address=v.address,
            service_type=v.service_type,
            status=v.status,
            created_at=v.created_at,
            employee_count=len(v.users)
        )
        for v in vendors
    ]

@router.post("/", response_model=VendorCompanyOut, status_code=status.HTTP_201_CREATED)
def create_vendor_company(
    vendor_in: VendorCompanyCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.COMPANY])),
    db: Session = Depends(get_db)
):
    """Register vendor company."""
    existing = db.query(VendorCompany).filter(VendorCompany.code == vendor_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vendor code already exists")

    vendor = VendorCompany(**vendor_in.model_dump())
    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    # Auto-associate vendor with current company if created by Company Admin
    if current_user.role == UserRole.COMPANY and current_user.company_id:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if company:
            company.vendors.append(vendor)
            db.commit()

    return VendorCompanyOut(
        id=vendor.id,
        name=vendor.name,
        code=vendor.code,
        email=vendor.email,
        phone=vendor.phone,
        address=vendor.address,
        service_type=vendor.service_type,
        status=vendor.status,
        created_at=vendor.created_at,
        employee_count=0
    )

@router.post("/{vendor_id}/assign-company/{company_id}")
def assign_vendor_to_company(
    vendor_id: int,
    company_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.COMPANY])),
    db: Session = Depends(get_db)
):
    """Assign vendor company to a client company."""
    vendor = db.query(VendorCompany).filter(VendorCompany.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor company not found")

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if vendor not in company.vendors:
        company.vendors.append(vendor)
        db.commit()

    return {"message": f"Vendor {vendor.name} assigned to {company.name}"}

@router.put("/{vendor_id}", response_model=VendorCompanyOut)
def update_vendor_company(
    vendor_id: int,
    vendor_in: VendorCompanyUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.VENDOR_COMPANY])),
    db: Session = Depends(get_db)
):
    """Update vendor company."""
    vendor = db.query(VendorCompany).filter(VendorCompany.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor company not found")

    if current_user.role == UserRole.VENDOR_COMPANY and current_user.vendor_company_id != vendor_id:
        raise HTTPException(status_code=403, detail="Cannot edit another vendor agency")

    for field, value in vendor_in.model_dump(exclude_unset=True).items():
        setattr(vendor, field, value)

    db.commit()
    db.refresh(vendor)

    return VendorCompanyOut(
        id=vendor.id,
        name=vendor.name,
        code=vendor.code,
        email=vendor.email,
        phone=vendor.phone,
        address=vendor.address,
        service_type=vendor.service_type,
        status=vendor.status,
        created_at=vendor.created_at,
        employee_count=len(vendor.users)
    )

@router.delete("/{vendor_id}")
def delete_vendor_company(
    vendor_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Delete vendor company."""
    vendor = db.query(VendorCompany).filter(VendorCompany.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor company not found")

    db.delete(vendor)
    db.commit()
    return {"message": "Vendor company deleted successfully"}
