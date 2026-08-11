from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models import Company, User, UserRole
from app.schemas import CompanyOut, CompanyCreate, CompanyUpdate

router = APIRouter()

@router.get("/", response_model=List[CompanyOut])
def list_companies(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List companies according to role permissions."""
    query = db.query(Company)
    
    if current_user.role == UserRole.ADMIN:
        companies = query.offset(skip).limit(limit).all()
    elif current_user.company_id:
        companies = query.filter(Company.id == current_user.company_id).all()
    else:
        companies = query.all()

    result = []
    for c in companies:
        result.append(CompanyOut(
            id=c.id,
            name=c.name,
            code=c.code,
            email=c.email,
            phone=c.phone,
            address=c.address,
            industry=c.industry,
            status=c.status,
            created_at=c.created_at,
            employee_count=len(c.users),
            vendor_count=len(c.vendors)
        ))
    return result

@router.post("/", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_company(
    company_in: CompanyCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Register a new company (Admin only)."""
    existing = db.query(Company).filter(Company.code == company_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company code already exists")

    company = Company(**company_in.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)

    return CompanyOut(
        id=company.id,
        name=company.name,
        code=company.code,
        email=company.email,
        phone=company.phone,
        address=company.address,
        industry=company.industry,
        status=company.status,
        created_at=company.created_at,
        employee_count=0,
        vendor_count=0
    )

@router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single company details."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if current_user.role != UserRole.ADMIN and current_user.company_id != company_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    return CompanyOut(
        id=company.id,
        name=company.name,
        code=company.code,
        email=company.email,
        phone=company.phone,
        address=company.address,
        industry=company.industry,
        status=company.status,
        created_at=company.created_at,
        employee_count=len(company.users),
        vendor_count=len(company.vendors)
    )

@router.put("/{company_id}", response_model=CompanyOut)
def update_company(
    company_id: int,
    company_in: CompanyUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.COMPANY])),
    db: Session = Depends(get_db)
):
    """Update company details."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if current_user.role == UserRole.COMPANY and current_user.company_id != company_id:
        raise HTTPException(status_code=403, detail="Cannot edit another company")

    for field, value in company_in.model_dump(exclude_unset=True).items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)

    return CompanyOut(
        id=company.id,
        name=company.name,
        code=company.code,
        email=company.email,
        phone=company.phone,
        address=company.address,
        industry=company.industry,
        status=company.status,
        created_at=company.created_at,
        employee_count=len(company.users),
        vendor_count=len(company.vendors)
    )

@router.delete("/{company_id}")
def delete_company(
    company_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Delete a company (Admin only)."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    db.delete(company)
    db.commit()
    return {"message": "Company deleted successfully"}
