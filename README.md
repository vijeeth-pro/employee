# Enterprise Employee & Vendor Management System

A full-stack enterprise workforce management platform featuring **FastAPI**, **PostgreSQL**, **JWT Authentication**, 5-tier **Role-Based Access Control (RBAC)**, **Ant Design (`antd`)**, **Zustand**, and **React Router v8**.

---

## 🌟 Key Features

- **Multi-Tenant RBAC Hierarchy**: 5-tier security roles (`admin`, `company`, `employee`, `vendor.company`, `vendor.employee`).
- **Database Auto-Seeding**: Initial sample data pre-populated for instant testing across all user roles.
- **Ant Design Modern UI**: Dark slate header banner, gradient statistic cards, interactive data tables, search/filters, and modals.
- **Single-Promise Session Deduplication**: Optimized state handling with Zustand selectors and React Router Protected Layout.

---

## 🏗️ Architecture & Project Structure

```text
employee/
├── backend/                  # FastAPI Backend API Service
│   ├── app/
│   │   ├── api/v1/          # REST Endpoint Routers (Employees, Companies, Vendors, Analytics)
│   │   ├── core/            # Database Session, Config, JWT Security, & RBAC Dependencies
│   │   ├── db/              # Initial Database Seeding & Schema Setup
│   │   ├── models/          # SQLAlchemy Models (User, Company, Vendor, Policy)
│   │   └── schemas/         # Pydantic Request/Response Models
│   ├── .env                 # Environment variables (Database URL, Secret Key)
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

# 3. Seed initial database records
python -m app.db.init_db

# 4. Start FastAPI server
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

## 🔑 Demo Login Accounts

| Role | Email | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin@system.com` | `admin123` | Global System Access |
| **Company Admin** | `company@apex.com` | `company123` | Organization & Employee Management |
| **Company Employee** | `employee@apex.com` | `emp123` | Personal Dashboard & Company Policies |
| **Vendor Admin** | `vendor@techserve.com` | `vendor123` | Vendor Agency & Contractor Management |
| **Vendor Contractor**| `vendoremp@techserve.com` | `vemp123` | Personal Contractor Profile & Rules |
