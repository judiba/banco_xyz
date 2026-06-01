from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, Response

from backend.api.v1.errors import ApiException
from backend.app_config.settings import settings
from backend.services import auth_service
from backend.services.saml_service import (
    SamlNotEnabledError,
    SamlValidationError,
    build_frontend_redirect_url,
    build_mock_saml_user,
    get_login_redirect_url,
    get_sp_metadata_xml,
    is_saml_dev_mock_enabled,
    is_saml_enabled,
    process_saml_response,
)

router = APIRouter(prefix="/auth/saml", tags=["auth-saml"])


def _saml_disabled() -> None:
    if not is_saml_enabled():
        raise ApiException(404, "AUTH_SAML_DISABLED", "Autenticação SAML não está habilitada.")


def _request_data_from_fastapi(request: Request, post_data: dict | None = None) -> dict:
    forwarded_proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    return {
        "https": "on" if forwarded_proto == "https" else "off",
        "http_host": request.headers.get("host", request.url.hostname or "localhost"),
        "script_name": request.url.path,
        "server_port": str(request.url.port or (443 if forwarded_proto == "https" else 80)),
        "get_data": dict(request.query_params),
        "post_data": post_data or {},
    }


@router.get("/login")
def saml_login(request: Request):
    """Redireciona ao Entra ID (prod) ou simula SSO em dev (APP_AUTH_SAML_DEV_MOCK)."""
    _saml_disabled()

    if is_saml_dev_mock_enabled():
        saml_user = build_mock_saml_user()
        user = auth_service.find_or_provision_saml_user(saml_user)
        access, refresh = auth_service.issue_tokens_for_user(user)
        return RedirectResponse(
            url=build_frontend_redirect_url(access, refresh),
            status_code=302,
        )

    try:
        redirect_url = get_login_redirect_url(_request_data_from_fastapi(request))
    except SamlValidationError as exc:
        raise ApiException(500, "AUTH_SAML_CONFIG_ERROR", str(exc)) from exc

    return RedirectResponse(url=redirect_url, status_code=302)


@router.post("/callback")
async def saml_callback(request: Request):
    """
    Recebe SAMLResponse do Entra ID (sem JWT).
    Provisiona usuário, emite tokens TTYD e redireciona ao front: /login?token=&refresh=
    """
    _saml_disabled()

    form = await request.form()
    post_data = {k: str(v) for k, v in form.items()}
    if "SAMLResponse" not in post_data:
        raise ApiException(422, "VALIDATION_ERROR", "SAMLResponse é obrigatório.")

    try:
        saml_user = process_saml_response(_request_data_from_fastapi(request, post_data))
    except SamlValidationError as exc:
        raise ApiException(
            401,
            "AUTH_SAML_INVALID_RESPONSE",
            str(exc),
        ) from exc

    user = auth_service.find_or_provision_saml_user(saml_user)
    access, refresh = auth_service.issue_tokens_for_user(user)
    return RedirectResponse(
        url=build_frontend_redirect_url(access, refresh),
        status_code=302,
    )


@router.get("/metadata", response_class=Response)
def saml_metadata():
    """XML de metadata do Service Provider para configurar Enterprise App no Entra."""
    _saml_disabled()
    try:
        xml = get_sp_metadata_xml()
    except SamlValidationError as exc:
        raise ApiException(500, "AUTH_SAML_CONFIG_ERROR", str(exc)) from exc

    return Response(content=xml, media_type="application/xml")
