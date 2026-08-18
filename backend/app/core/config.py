import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Employee & Vendor Management API"
    API_V1_STR: str = "/api/v1"
    
    # Security Secrets (Strictly loaded from .env)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database Connection (Strictly loaded from .env)
    POSTGRES: str
    
    # RAG System Configuration (Gemini & Pinecone - Loaded from .env)
    GEMINI_API_KEY: str = ""
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "workforce-policy-index"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
