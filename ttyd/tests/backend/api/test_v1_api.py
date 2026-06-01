import pytest
from fastapi.testclient import TestClient

from backend.infrastructure.persistence.memory_store import reset_memory_store
from backend.main import app


@pytest.fixture(autouse=True)
def reset_store():
    reset_memory_store()
    from backend.infrastructure.persistence import factory

    factory._store = None
    yield
    factory._store = None


@pytest.fixture
def client():
    return TestClient(app)


def _login(client: TestClient) -> str:
    resp = client.post(
        "/v1/auth/login",
        json={"username": "adminrecord", "password": "record123"},
    )
    assert resp.status_code == 200
    return resp.json()["tokens"]["accessToken"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_login_invalid_credentials(client):
    resp = client.post(
        "/v1/auth/login",
        json={"username": "adminrecord", "password": "wrong"},
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "AUTH_INVALID_CREDENTIALS"


def test_bootstrap(client):
    token = _login(client)
    resp = client.get("/v1/session/bootstrap", headers=_auth(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["displayName"] == "Diego"
    assert len(data["conversations"]["data"]) >= 1
    assert len(data["folders"]["data"]) >= 1
    assert data["assistant"]["displayName"] == "RecordAI"


def test_conversations_crud(client):
    token = _login(client)
    headers = _auth(token)

    create = client.post(
        "/v1/conversations",
        json={"title": "Novo chat"},
        headers=headers,
    )
    assert create.status_code == 201
    conv_id = create.json()["id"]

    patch = client.patch(
        f"/v1/conversations/{conv_id}",
        json={"title": "Título atualizado"},
        headers=headers,
    )
    assert patch.status_code == 200
    assert patch.json()["title"] == "Título atualizado"

    delete = client.delete(f"/v1/conversations/{conv_id}", headers=headers)
    assert delete.status_code == 204


def test_send_message_dev_offline(client):
    token = _login(client)
    headers = _auth(token)

    create = client.post("/v1/conversations", json={}, headers=headers)
    conv_id = create.json()["id"]

    msg = client.post(
        f"/v1/conversations/{conv_id}/messages",
        json={"content": "Qual o share de ontem?"},
        headers=headers,
    )
    assert msg.status_code == 201
    body = msg.json()
    assert body["userMessage"]["role"] == "user"
    assert body["assistantMessage"]["role"] == "assistant"
    assert "Entendi" in body["assistantMessage"]["content"] or len(
        body["assistantMessage"]["content"]
    ) > 0


def test_with_message_creates_conversation(client):
    token = _login(client)
    headers = _auth(token)

    resp = client.post(
        "/v1/conversations/with-message",
        json={"content": "Primeira pergunta do usuário"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["conversation"]["description"] == "Primeira pergunta do usuário"


def test_folders_duplicate_name(client):
    token = _login(client)
    headers = _auth(token)

    client.post("/v1/folders", json={"name": "Pasta Teste"}, headers=headers)
    dup = client.post("/v1/folders", json={"name": "Pasta Teste"}, headers=headers)
    assert dup.status_code == 409
    assert dup.json()["error"]["code"] == "FOLDER_DUPLICATE_NAME"


def test_message_feedback(client):
    token = _login(client)
    headers = _auth(token)
    bootstrap = client.get("/v1/session/bootstrap", headers=headers).json()
    conv_id = bootstrap["conversations"]["data"][0]["id"]
    messages = client.get(
        f"/v1/conversations/{conv_id}/messages",
        headers=headers,
    ).json()["data"]
    assistant = next(m for m in messages if m["role"] == "assistant")

    fb = client.put(
        f"/v1/messages/{assistant['id']}/feedback",
        json={"feedback": "like"},
        headers=headers,
    )
    assert fb.status_code == 200
    assert fb.json()["feedback"] == "like"


def test_export_txt(client):
    token = _login(client)
    headers = _auth(token)
    conv_id = client.get("/v1/session/bootstrap", headers=headers).json()["conversations"]["data"][0]["id"]
    resp = client.get(
        f"/v1/conversations/{conv_id}/export?format=txt",
        headers=headers,
    )
    assert resp.status_code == 200
    assert "Exportação de conversa" in resp.text
