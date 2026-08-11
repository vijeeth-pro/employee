from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.models import User
from app.schemas import Token, LoginRequest, UserOut
from app.core.deps import get_current_user

router = APIRouter()

@router.post("/login", response_model=Token)
def login(
    response: Response,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user, return JWT bearer token AND set HttpOnly SameSite Cookie."""
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )

    # Set HttpOnly Cookie for security (Prevents XSS token theft)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # Set to True in HTTPS production
    )

    return {"access_token": token, "token_type": "bearer"}

@router.post("/logout")
def logout(response: Response):
    """Clear HttpOnly access_token cookie."""
    response.delete_cookie(key="access_token", path="/", httponly=True, samesite="lax")
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    company_name = current_user.company.name if current_user.company else None
    vendor_name = current_user.vendor_company.name if current_user.vendor_company else None
    
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        company_id=current_user.company_id,
        vendor_company_id=current_user.vendor_company_id,
        phone=current_user.phone,
        designation=current_user.designation,
        department=current_user.department,
        status=current_user.status,
        created_at=current_user.created_at,
        company_name=company_name,
        vendor_company_name=vendor_name
    )
