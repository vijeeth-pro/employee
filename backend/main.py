from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.db.init_db import init_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Employee & Vendor Management API with multi-tenancy and HttpOnly cookie security."
)

# Set up CORS middleware with explicit origins for credentials/cookies support
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://localhost:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to ensure tables exist
@app.on_event("startup")
def startup_event():
    try:
        init_db()
    except Exception as e:
        print("Startup DB init message:", e)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "status": "success",
        "message": "Employee & Vendor Management API is running!",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }
