import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Employee & Vendor Management API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "super_secret_jwt_key_employee_management_2026_antigravity"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    POSTGRES: str = os.getenv("POSTGRES", "postgresql://vijeethsankar@localhost:5432/test_db")
    GEMINI_API_KEY: str = ""

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
