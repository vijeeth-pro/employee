# Enterprise Employee & Vendor Management System

A full-stack enterprise workforce management platform featuring **FastAPI**, **PostgreSQL**, **JWT Authentication**, 5-tier **Role-Based Access Control (RBAC)**, **Google Gemini AI RAG Engine**, **Ant Design (`antd`)**, **Zustand**, and **React Router v8**.

---

## 🌟 Key Features

- **Multi-Tenant RBAC Hierarchy**: 5-tier security roles (`admin`, `company`, `employee`, `vendor.company`, `vendor.employee`).
- **AI RAG Assistant Engine**: Integrated with **Google Gemini (`gemini-2.5-flash`)** and contextual RAG vector retrieval with role-scoped document security.
- **Database Auto-Seeding**: Initial sample data pre-populated for instant testing across all user roles.
- **Ant Design Modern UI**: Dark slate header banner, gradient statistic cards, interactive data tables, search/filters, and modals.
- **Single-Promise Session Deduplication**: Optimized state handling with Zustand selectors and React Router Protected Layout.

---

## 🏗️ Architecture & Project Structure

```text
employee/
├── backend/                  # FastAPI Backend API Service
│   ├── app/
│   │   ├── api/v1/          # REST Endpoint Routers (Employees, Companies, Vendors, AI, Analytics)
│   │   ├── core/            # Database Session, Config, JWT Security, & RBAC Dependencies
│   │   ├── db/              # Initial Database Seeding & Schema Setup
│   │   ├── models/          # SQLAlchemy Models (User, Company, Vendor, Policy)
│   │   ├── schemas/         # Pydantic Request/Response Models
│   │   └── services/        # AI Service & RAG Vector Engine
│   ├── .env                 # Environment variables (Database URL, Secret Key, Gemini API Key)
│   ├── main.py              # FastAPI Application Entrypoint
│   ├── requirements.txt     # Python Dependencies
│   └── verify_system.py     # System Verification Test Suite
└── web/                     # React Frontend Application (React Router v8 + Ant Design)
    ├── app/                 # Components, Pages, Stores (Zustand), & Layouts
    ├── package.json         # Node.js Dependencies
    └── vite.config.ts       # Vite Configuration
```

---

## 🛠️ Quick Installation & Setup Guide

### 1. Backend Setup (`/backend`)

```bash
cd backend

# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure .env file
# Ensure backend/.env contains:
# POSTGRES=postgresql://vijeethsankar@localhost:5432/test_db
# GEMINI_API_KEY=<your_gemini_api_key>

# 4. Seed initial database records
python -m app.db.init_db

# 5. Start FastAPI server
fastapi dev main.py
```

Backend API runs at: **`http://localhost:8000`** | Interactive OpenAPI Docs: **`http://localhost:8000/docs`**

---

### 2. Frontend Setup (`/web`)

```bash
cd web

# 1. Install dependencies
npm install

# 2. Start Vite development server
npm run dev
```

Frontend application runs at: **`http://localhost:5173`**

---

## 🤖 AI Assistant & RAG Engine

The backend includes a RAG (Retrieval-Augmented Generation) Engine powered by **Google Gemini API** (`gemini-2.5-flash`):

- **Vector Chunks**: Documents, policies, company details, and employee profiles are indexed into vector chunks.
- **RBAC Security**: Chunks are strictly filtered according to the user's role before context synthesis.
- **API Key Configuration**: Set `GEMINI_API_KEY` in `backend/.env`.

---

## 🔑 Demo Login Accounts

| Role | Email | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin@system.com` | `admin123` | Global System Access |
| **Company Admin** | `company@apex.com` | `company123` | Organization & Employee Management |
| **Company Employee** | `employee@apex.com` | `emp123` | Personal Dashboard & Company Policies |
| **Vendor Admin** | `vendor@techserve.com` | `vendor123` | Vendor Agency & Contractor Management |
| **Vendor Contractor**| `vendoremp@techserve.com` | `vemp123` | Personal Contractor Profile & Rules |
