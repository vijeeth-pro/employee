import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve absolute path to .env file in backend directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Employee & Vendor Management API"
    API_V1_STR: str = "/api/v1"
    
    # Security Secrets (Loads from system env or .env file with safe fallback)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "e8391b4028682a8847b744d0ecf4db89694cbe8499252063fb55a1aa80c4ab63")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database Connection (Loads from system env or .env file with safe fallback)
    POSTGRES: str = os.getenv("POSTGRES", "postgresql://postgres:postgres@localhost:5432/employee_db")
    
    # RAG System Configuration (Loaded from .env file)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "workforce-policy-index")

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH if os.path.exists(ENV_FILE_PATH) else ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

