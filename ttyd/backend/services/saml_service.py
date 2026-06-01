"""Serviço SAML 2.0 — TTYD como SP, Microsoft Entra ID (Record) como IdP."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

from backend.app_config.settings import settings


class SamlNotEnabledError(Exception):
    pass


class SamlValidationError(Exception):
    def __init__(self, message: str, errors: list[str] | None = None):
        super().__init__(message)
        self.errors = errors or []


@dataclass
class SamlUserData:
    name_id: str
    email: str | None
    display_name: str | None
    given_name: str | None
    surname: str | None
    attributes: dict[str, Any]


def is_saml_enabled() -> bool:
    return settings.APP_AUTH_SAML_ENABLED


def is_saml_dev_mock_enabled() -> bool:
    """Login SAML sem IdP Record — só com DEV_OFFLINE (evita uso em prod)."""
    return (
        settings.APP_AUTH_SAML_ENABLED
        and settings.APP_AUTH_SAML_DEV_MOCK
        and settings.DEV_OFFLINE
    )


def build_mock_saml_user() -> SamlUserData:
    """Usuário SSO fictício para testar fluxo igual ao callback real."""
    email = settings.APP_AUTH_SAML_MOCK_EMAIL.strip()
    display = settings.APP_AUTH_SAML_MOCK_DISPLAY_NAME.strip() or email
    parts = display.split(None, 1)
    given = parts[0] if parts else None
    surname = parts[1] if len(parts) > 1 else None
    return SamlUserData(
        name_id=email,
        email=email,
        display_name=display,
        given_name=given,
        surname=surname,
        attributes={
            "email": [email],
            "displayName": [display],
            "userPrincipalName": [email],
        },
    )


def _require_enabled() -> None:
    if not is_saml_enabled():
        raise SamlNotEnabledError("SAML authentication is not enabled.")


def normalize_x509_cert(cert: str) -> str:
    """Certificado Record pode vir sem header/footer PEM."""
    if not cert:
        return ""
    cleaned = cert.strip().replace("-----BEGIN CERTIFICATE-----", "")
    cleaned = cleaned.replace("-----END CERTIFICATE-----", "")
    cleaned = "".join(cleaned.split())
    if not cleaned:
        return ""
    lines = [cleaned[i : i + 64] for i in range(0, len(cleaned), 64)]
    return "-----BEGIN CERTIFICATE-----\n" + "\n".join(lines) + "\n-----END CERTIFICATE-----"


def build_saml_settings() -> dict[str, Any]:
    _require_enabled()
    base_url = os.getenv("APP_AUTH_SAML_BASE_URL", "http://localhost:8000")
    return {
        "strict": True,
        "debug": settings.APP_ENV == "dev",
        "sp": {
            "entityId": settings.APP_AUTH_SAML_SP_ENTITY_ID,
            "assertionConsumerService": {
                "url": settings.APP_AUTH_SAML_SP_ACS_URL,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            "singleLogoutService": {
                "url": settings.APP_AUTH_SAML_SP_SLO_URL or f"{base_url}/v1/auth/saml/logout",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "NameIDFormat": settings.APP_AUTH_SAML_NAME_ID_FORMAT,
        },
        "idp": {
            "entityId": settings.APP_AUTH_SAML_IDP_ENTITY_ID,
            "singleSignOnService": {
                "url": settings.APP_AUTH_SAML_IDP_SSO_URL,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "x509cert": normalize_x509_cert(settings.APP_AUTH_SAML_IDP_CERT),
        },
        "security": {
            "wantAssertionsSigned": True,
            "wantMessagesSigned": True,
            "authnRequestsSigned": False,
            "logoutRequestSigned": False,
            "logoutResponseSigned": False,
        },
    }


def _prepare_request(request_data: dict[str, str]) -> dict[str, str]:
    return {
        "https": request_data.get("https", "off"),
        "http_host": request_data.get("http_host", "localhost"),
        "script_name": request_data.get("script_name", ""),
        "server_port": request_data.get("server_port", "8000"),
        "get_data": request_data.get("get_data", {}),
        "post_data": request_data.get("post_data", {}),
    }


def get_login_redirect_url(request_data: dict[str, str]) -> str:
    _require_enabled()
    from onelogin.saml2.auth import OneLogin_Saml2_Auth

    auth = OneLogin_Saml2_Auth(_prepare_request(request_data), build_saml_settings())
    return auth.login()


def process_saml_response(request_data: dict[str, str]) -> SamlUserData:
    _require_enabled()
    from onelogin.saml2.auth import OneLogin_Saml2_Auth

    auth = OneLogin_Saml2_Auth(_prepare_request(request_data), build_saml_settings())
    auth.process_response()
    errors = auth.get_errors()
    if errors:
        reason = auth.get_last_error_reason() or ""
        raise SamlValidationError(
            f"SAML validation failed: {', '.join(errors)}. {reason}".strip(),
            errors=errors,
        )
    if not auth.is_authenticated():
        raise SamlValidationError("SAML response did not authenticate the user.")

    attributes = auth.get_attributes() or {}
    name_id = auth.get_nameid() or ""
    email = (
        _first_attr(attributes, "email")
        or _first_attr(attributes, "userPrincipalName")
        or name_id
    )
    given = _first_attr(attributes, "givenName")
    surname = _first_attr(attributes, "surname")
    display = _first_attr(attributes, "displayName") or _join_names(given, surname) or email

    return SamlUserData(
        name_id=name_id,
        email=email,
        display_name=display,
        given_name=given,
        surname=surname,
        attributes=attributes,
    )


def get_sp_metadata_xml() -> str:
    _require_enabled()
    from onelogin.saml2.auth import OneLogin_Saml2_Auth
    from onelogin.saml2.settings import OneLogin_Saml2_Settings

    saml_settings = OneLogin_Saml2_Settings(settings=build_saml_settings(), sp_validation_only=True)
    metadata = saml_settings.get_sp_metadata()
    errors = saml_settings.validate_metadata(metadata)
    if errors:
        raise SamlValidationError(f"Invalid SP metadata: {', '.join(errors)}", errors=errors)
    return metadata


def build_frontend_redirect_url(access_token: str, refresh_token: str) -> str:
    base = settings.APP_AUTH_SAML_FRONTEND_LOGIN_URL.rstrip("/")
    query = urlencode({"token": access_token, "refresh": refresh_token})
    return f"{base}?{query}"


def _first_attr(attributes: dict[str, Any], key: str) -> str | None:
    value = attributes.get(key)
    if value is None:
        return None
    if isinstance(value, list):
        return str(value[0]) if value else None
    return str(value)


def _join_names(given: str | None, surname: str | None) -> str | None:
    parts = [p for p in (given, surname) if p]
    return " ".join(parts) if parts else None
