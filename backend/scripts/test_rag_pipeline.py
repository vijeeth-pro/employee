import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app
from app.db.init_db import init_db

def test_rag():
    print("=== Testing RAG System Pipeline ===")
    init_db()
    client = TestClient(app)

    # 1. Login as Employee
    login_res = client.post("/api/v1/auth/login", json={"email": "employee@apex.com", "password": "emp123"})
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    print("Employee login successful.")

    # 2. Ask RAG Chat question
    query_payload = {"message": "How many annual leave days do I have and what are the rules?"}
    chat_res = client.post("/api/v1/rag/chat", json=query_payload)
    assert chat_res.status_code == 200, f"RAG chat failed: {chat_res.text}"
    
    data = chat_res.json()
    print("\n--- AI Assistant Response ---")
    print(data["answer"])
    print("\n--- Referenced Sources ---")
    for s in data.get("sources", []):
        print(f"[{s['score']}] {s['title']} ({s['source_type']})")

    print("\n>>> RAG PIPELINE TEST PASSED CLEANLY! <<<")

if __name__ == "__main__":
    test_rag()
