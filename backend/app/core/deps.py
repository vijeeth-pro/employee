from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import User, UserRole
from app.schemas import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token_header: str = Depends(oauth2_scheme)
) -> User:
    """Extract JWT token from HttpOnly cookie first, then fallback to Authorization header."""
    token = request.cookies.get("access_token")
    if not token and token_header:
        token = token_header
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenPayload(sub=user_id)
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(token_data.sub)).first()
    if user is None:
        raise credentials_exception

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )

    return user

def require_role(allowed_roles: list[UserRole]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{current_user.role.value}' does not have sufficient permissions."
            )
        return current_user
    return role_checker
