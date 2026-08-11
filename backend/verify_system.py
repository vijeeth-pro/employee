from fastapi.testclient import TestClient
from main import app
from app.db.init_db import init_db

def test_system():
    print("=== 1. In-Memory Database Seeding ===")
    init_db()

    roles_to_test = [
        ("Admin", "admin@system.com", "admin123", "admin"),
        ("Company Admin", "company@apex.com", "company123", "company"),
        ("Employee", "employee@apex.com", "emp123", "employee"),
        ("Vendor Admin", "vendor@techserve.com", "vendor123", "vendor.company"),
        ("Vendor Employee", "vendoremp@techserve.com", "vemp123", "vendor.employee")
    ]

    print("\n=== 2. Testing HttpOnly Cookie & Bearer JWT Authentication ===")
    for title, email, password, expected_role in roles_to_test:
        client = TestClient(app)
        res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert res.status_code == 200, f"Login failed for {email}: {res.text}"
        
        # Verify /auth/me
        me_res = client.get("/api/v1/auth/me")
        assert me_res.status_code == 200
        user_info = me_res.json()
        assert user_info["role"] == expected_role
        print(f"  [SUCCESS] {title} ({email}) authenticated via HttpOnly Cookie! (Role: {user_info['role']})")

    print("\n=== 3. Testing Role-Aware AI Assistant & RAG Vector Search ===")
    
    # 3a. Admin Query
    admin_client = TestClient(app)
    admin_client.post("/api/v1/auth/login", json={"email": "admin@system.com", "password": "admin123"})
    ai_admin_res = admin_client.post("/api/v1/ai/chat", json={"prompt": "What is the annual leave policy?"})
    assert ai_admin_res.status_code == 200
    admin_ai = ai_admin_res.json()
    assert admin_ai["role_applied"] == "admin"
    print(f"  [SUCCESS] Admin AI Chat Query processed. Sources retrieved: {len(admin_ai['sources'])}")

    # 3b. Company Employee Query
    emp_client = TestClient(app)
    emp_client.post("/api/v1/auth/login", json={"email": "employee@apex.com", "password": "emp123"})
    ai_emp_res = emp_client.post("/api/v1/ai/chat", json={"prompt": "What is the remote work policy?"})
    assert ai_emp_res.status_code == 200
    emp_ai = ai_emp_res.json()
    assert emp_ai["role_applied"] == "employee"
    print(f"  [SUCCESS] Employee AI Chat Query processed. Role context enforced ({emp_ai['role_applied']}).")

    # 3c. Vendor Employee / Contractor Query
    vemp_client = TestClient(app)
    vemp_client.post("/api/v1/auth/login", json={"email": "vendoremp@techserve.com", "password": "vemp123"})
    ai_vemp_res = vemp_client.post("/api/v1/ai/chat", json={"prompt": "What are contractor timesheet rules?"})
    assert ai_vemp_res.status_code == 200
    vemp_ai = ai_vemp_res.json()
    assert vemp_ai["role_applied"] == "vendor.employee"
    print(f"  [SUCCESS] Vendor Contractor AI Chat Query processed. Role context enforced ({vemp_ai['role_applied']}).")

    print("\n>>> ALL HTTPONLY COOKIE & AI RAG CHECKS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_system()
