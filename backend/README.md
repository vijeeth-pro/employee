# Employee & Vendor Management Backend API

FastAPI REST API backend with PostgreSQL database, SQLAlchemy ORM, JWT authentication, 5-tier role-based access control (RBAC), Google Gemini RAG Engine integration, and automated initial database seeding.

---

## 🛠️ Required Libraries & Dependencies

All dependencies are defined in `requirements.txt`:

| Package | Version | Purpose |
| :--- | :--- | :--- |
| `fastapi` | `>=0.110.0` | High-performance Python web framework |
| `uvicorn` | `>=0.28.0` | ASGI server for running FastAPI |
| `sqlalchemy` | `>=2.0.28` | Database ORM & SQL toolkit |
| `psycopg2-binary` | `>=2.9.9` | PostgreSQL database driver |
| `pyjwt` | `>=2.8.0` | JWT token generation & verification |
| `passlib[bcrypt]` | `>=1.7.4` | Secure password hashing framework |
| `bcrypt` | `>=4.1.2` | Bcrypt hashing algorithm |
| `pydantic` | `>=2.6.4` | Data validation schema framework |
| `pydantic-settings` | `>=2.2.1` | Environment settings management |
| `email-validator` | `>=2.1.1` | Email format validation |
| `python-dotenv` | `>=1.0.1` | `.env` configuration file loader |
| `requests` | `>=2.31.0` | HTTP client for automated testing |
| `google-generativeai`| `>=0.5.0` | Google Gemini LLM API client for RAG synthesis |

---

## 🚀 Step-by-Step Installation & Setup Process

### 1. Prerequisite
Ensure Python 3.10+ and PostgreSQL are installed and running locally.

### 2. Create and Activate Virtual Environment
Inside the `backend` directory, run:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment (macOS/Linux)
source .venv/bin/activate

# On Windows:
# .venv\Scripts\activate
```

### 3. Install All Backend Dependencies
Install all required libraries using `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Configure `.env` File
Create or update `backend/.env`:

```env
POSTGRES=postgresql://vijeethsankar@localhost:5432/test_db
SECRET_KEY=super_secret_jwt_key_employee_management_2026_antigravity
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Initialize & Seed Database
Populate database tables and pre-configured sample users for all 5 roles:

```bash
python -m app.db.init_db
```

### 6. Run FastAPI Development Server
Start the development server with auto-reload:

```bash
fastapi dev main.py
```
*or alternatively:*
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at: **`http://localhost:8000`**
Interactive OpenAPI Docs: **`http://localhost:8000/docs`**

---

## 🧪 Running Verification Tests

Run the automated test suite verifying DB tables, JWT authentication, and RBAC security:

```bash
python verify_system.py
```
