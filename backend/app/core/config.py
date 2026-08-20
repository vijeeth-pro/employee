import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve absolute path to .env file in backend directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Employee & Vendor Management API"
    API_V1_STR: str = "/api/v1"
    
    # Security Secrets (Strictly loaded from .env file)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database Connection (Strictly loaded from .env file)
    POSTGRES: str
    
    # RAG System Configuration (Strictly loaded from .env file)
    GEMINI_API_KEY: str = ""
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "workforce-policy-index"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH if os.path.exists(ENV_FILE_PATH) else ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

