import os
from msal import ConfidentialClientApplication

# Variáveis de ambiente (serão carregadas do .env correspondente)
TENANT_ID = os.getenv("ENTRA_TENANT_ID")
CLIENT_ID = os.getenv("ENTRA_CLIENT_ID")
CLIENT_SECRET = os.getenv("ENTRA_CLIENT_SECRET")  # Deve ser mantido em segredo!
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = os.getenv("ENTRA_REDIRECT_URI", "http://localhost:8000/v1/auth/callback")


def get_msal_app():
    return ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )


def get_auth_url():
    """Gera a URL de redirecionamento para login na Microsoft"""
    app = get_msal_app()
    return app.get_authorization_request_url(scopes=["User.Read"], redirect_uri=REDIRECT_URI)


def acquire_token_by_code(code: str):
    """Troca o código de autorização pelo token de acesso"""
    app = get_msal_app()
    result = app.acquire_token_by_authorization_code(
        code, scopes=["User.Read"], redirect_uri=REDIRECT_URI
    )
    return result
