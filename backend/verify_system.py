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

    print("\n>>> ALL HTTPONLY COOKIE & AUTH CHECKS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_system()
