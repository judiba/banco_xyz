from fastapi.testclient import TestClient
from backend.main import app


def test_chat_endpoint():
    client = TestClient(app)
    response = client.post("/chat", json={"message": "Olá", "org_id": "test-org"})
    assert response.status_code == 200
    assert "response" in response.json()
    print("\n✅ Test /chat: PASSED")


if __name__ == "__main__":
    test_chat_endpoint()
