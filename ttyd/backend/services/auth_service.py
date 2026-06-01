from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from backend.api.v1.errors import ApiException
from backend.api.v1.schemas.common import ErrorDetail
from backend.app_config.settings import settings
from backend.infrastructure.persistence.factory import get_store
from backend.infrastructure.persistence.models import UserRecord
from backend.services.saml_service import SamlUserData

ALGORITHM = "HS256"


def _hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(user_id: str, username: str, roles: list[str]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_ACCESS_EXPIRE_SECONDS)
    payload = {
        "sub": user_id,
        "username": username,
        "roles": roles,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> tuple[str, str]:
    raw = secrets.token_urlsafe(48)
    token_id = _hash_refresh_token(raw)
    expires_at = int(
        (datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_REFRESH_EXPIRE_SECONDS)).timestamp()
        * 1000
    )
    get_store().save_refresh_token(token_id, user_id, expires_at)
    return raw, token_id


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise JWTError("invalid type")
        return payload
    except JWTError as exc:
        raise ApiException(401, "AUTH_TOKEN_EXPIRED", "Token expirado ou inválido.") from exc


def issue_tokens_for_user(user: UserRecord) -> tuple[str, str]:
    access = create_access_token(user.id, user.username, user.roles)
    refresh, _ = create_refresh_token(user.id)
    return access, refresh


def login(username: str, password: str) -> tuple[UserRecord, str, str]:
    store = get_store()
    user = store.get_user_by_username(username.strip())
    if not user:
        raise ApiException(
            401,
            "AUTH_INVALID_CREDENTIALS",
            "Usuário ou senha inválidos.",
        )
    if not user.is_active:
        raise ApiException(
            403,
            "AUTH_ACCOUNT_INACTIVE",
            "Conta desativada. Contate o administrador.",
        )
    if user.auth_provider == "microsoft" or not store.verify_password(user, password):
        raise ApiException(
            401,
            "AUTH_INVALID_CREDENTIALS",
            "Usuário ou senha inválidos.",
        )
    access, refresh = issue_tokens_for_user(user)
    return user, access, refresh


def find_or_provision_saml_user(saml_user: SamlUserData) -> UserRecord:
    """Busca ou cria usuário SSO (auth_provider=microsoft, ad_oid=name_id)."""
    store = get_store()
    user = store.get_user_by_ad_oid(saml_user.name_id)

    if user:
        if not user.is_active:
            raise ApiException(
                403,
                "AUTH_ACCOUNT_INACTIVE",
                "Conta desativada. Contate o administrador.",
            )
        return user

    if not settings.APP_AUTH_SAML_AUTO_PROVISION:
        raise ApiException(
            403,
            "AUTH_SAML_PROVISION_DISABLED",
            "Usuário não autorizado. O provisionamento automático está desativado.",
        )

    username = _derive_username(saml_user)
    display_name = saml_user.display_name or username
    return store.create_saml_user(
        ad_oid=saml_user.name_id,
        username=username,
        email=saml_user.email,
        display_name=display_name,
        role=settings.APP_AUTH_SAML_DEFAULT_ROLE,
        tenant_id="record-br",
    )


def _derive_username(saml_user: SamlUserData) -> str:
    if saml_user.email and "@" in saml_user.email:
        return saml_user.email.split("@")[0].lower()
    return saml_user.name_id.lower().replace("@", "_at_")


def refresh_tokens(refresh_token: str) -> tuple[str, str | None]:
    store = get_store()
    token_id = _hash_refresh_token(refresh_token)
    record = store.get_refresh_token(token_id)
    if not record:
        raise ApiException(401, "AUTH_TOKEN_EXPIRED", "Refresh token inválido.")
    if record.get("expiresAt", 0) < int(datetime.now(timezone.utc).timestamp() * 1000):
        store.delete_refresh_token(token_id)
        raise ApiException(401, "AUTH_TOKEN_EXPIRED", "Refresh token expirado.")
    user = store.get_user(record["userId"])
    if not user:
        raise ApiException(401, "AUTH_TOKEN_EXPIRED", "Usuário não encontrado.")
    store.delete_refresh_token(token_id)
    access = create_access_token(user.id, user.username, user.roles)
    new_refresh, _ = create_refresh_token(user.id)
    return access, new_refresh


def logout(refresh_token: str | None) -> None:
    if refresh_token:
        get_store().delete_refresh_token(_hash_refresh_token(refresh_token))


def get_current_user(user_id: str) -> UserRecord:
    user = get_store().get_user(user_id)
    if not user:
        raise ApiException(401, "AUTH_TOKEN_EXPIRED", "Usuário não encontrado.")
    return user
