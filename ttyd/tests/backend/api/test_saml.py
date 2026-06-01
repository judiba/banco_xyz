import pytest
from fastapi.testclient import TestClient

from backend.infrastructure.persistence.memory_store import reset_memory_store
from backend.main import app
from backend.services import auth_service
from backend.services.saml_service import SamlUserData


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


def test_saml_login_disabled_by_default(client, monkeypatch):
    monkeypatch.setenv("APP_AUTH_SAML_ENABLED", "false")
    from backend.app_config import settings as settings_module

    settings_module.settings.APP_AUTH_SAML_ENABLED = False

    resp = client.get("/v1/auth/saml/login", follow_redirects=False)
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "AUTH_SAML_DISABLED"


def test_saml_callback_without_body_returns_422(client, monkeypatch):
    monkeypatch.setenv("APP_AUTH_SAML_ENABLED", "true")
    from backend.app_config import settings as settings_module

    s = settings_module.settings
    s.APP_AUTH_SAML_ENABLED = True
    s.APP_AUTH_SAML_IDP_ENTITY_ID = "https://idp.example.com"
    s.APP_AUTH_SAML_IDP_SSO_URL = "https://idp.example.com/sso"
    s.APP_AUTH_SAML_IDP_CERT = "MIIC..."  # will fail on real validation if called

    resp = client.post("/v1/auth/saml/callback")
    assert resp.status_code == 422


def test_find_or_provision_saml_user_auto_provision(monkeypatch):
    monkeypatch.setenv("APP_AUTH_SAML_ENABLED", "true")
    from backend.app_config import settings as settings_module

    s = settings_module.settings
    s.APP_AUTH_SAML_AUTO_PROVISION = True
    s.APP_AUTH_SAML_DEFAULT_ROLE = "ttyd:user"

    data = SamlUserData(
        name_id="diego.silva@record.com.br",
        email="diego.silva@record.com.br",
        display_name="Diego Silva",
        given_name="Diego",
        surname="Silva",
        attributes={},
    )
    user = auth_service.find_or_provision_saml_user(data)
    assert user.ad_oid == "diego.silva@record.com.br"
    assert user.auth_provider == "microsoft"
    assert user.is_active is True
    assert user.must_change_password is False
    assert user.roles == ["ttyd:user"]

    again = auth_service.find_or_provision_saml_user(data)
    assert again.id == user.id


def test_find_or_provision_blocks_when_auto_provision_off(monkeypatch):
    from backend.app_config import settings as settings_module

    s = settings_module.settings
    s.APP_AUTH_SAML_AUTO_PROVISION = False

    data = SamlUserData(
        name_id="unknown@record.com.br",
        email="unknown@record.com.br",
        display_name="Unknown",
        given_name=None,
        surname=None,
        attributes={},
    )
    from backend.api.v1.errors import ApiException

    with pytest.raises(ApiException) as exc:
        auth_service.find_or_provision_saml_user(data)
    assert exc.value.status_code == 403
    assert exc.value.code == "AUTH_SAML_PROVISION_DISABLED"


def test_saml_dev_mock_login_redirects_to_frontend(client, monkeypatch):
    from backend.app_config import settings as settings_module

    s = settings_module.settings
    s.APP_AUTH_SAML_ENABLED = True
    s.APP_AUTH_SAML_DEV_MOCK = True
    s.DEV_OFFLINE = True
    s.APP_AUTH_SAML_AUTO_PROVISION = True
    s.APP_AUTH_SAML_FRONTEND_LOGIN_URL = "http://localhost:4200/login"
    s.APP_AUTH_SAML_MOCK_EMAIL = "sso.mock@record.com.br"

    resp = client.get("/api/auth/saml/login", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"].startswith("http://localhost:4200/login?")
    assert "token=" in resp.headers["location"]
    assert "refresh=" in resp.headers["location"]


def test_api_auth_saml_mirror_path_disabled(client, monkeypatch):
    """Rota /api/auth/saml/* espelha ContentAI."""
    monkeypatch.setenv("APP_AUTH_SAML_ENABLED", "false")
    from backend.app_config import settings as settings_module

    settings_module.settings.APP_AUTH_SAML_ENABLED = False

    resp = client.get("/api/auth/saml/login", follow_redirects=False)
    assert resp.status_code == 404
