from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

## ENVIRONMENT

BASE_DIR = Path(__file__).resolve().parent  # app_config
PROJECT_ROOT = BASE_DIR.parent.parent  # raiz do projeto

ENV_NAME = os.getenv("APP_ENV", "dev")
ENV_FILE = PROJECT_ROOT / "security" / f".env.{ENV_NAME}"

load_dotenv(ENV_FILE if ENV_FILE.exists() else PROJECT_ROOT / ".env")

print(f"⚙️ Loading environment: {ENV_NAME}")
print(f"📄 ENV file: {ENV_FILE}")


class Settings:
    APP_ENV: str = ENV_NAME
    DEV_OFFLINE: bool = os.getenv("DEV_OFFLINE", "false").lower() == "true"

    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_PROFILE: str | None = os.getenv("AWS_PROFILE")

    LLM_MODEL: str = os.getenv(
        "LLM_MODEL",
        "us.anthropic.claude-sonnet-4-20250514-v1:0",
    )
    ### RAG
    RAG_BUCKET: str = os.getenv("RAG_BUCKET", "")
    RAG_KEY: str = os.getenv("RAG_KEY", "")
    SQL_KEY: str = os.getenv("SQL_KEY", "")
    ### REDSHIFT
    REDSHIFT_LAMBDA_ARN: str = os.getenv("REDSHIFT_LAMBDA_ARN", "")
    ### PROMPTS
    YAML_PATH_TABLES: str = os.getenv("YAML_PATH_TABLES", "backend/app_config/desc_tables.yaml")

    YAML_PATH_COL: str = os.getenv("YAML_PATH_COL", "backend/app_config/desc_colunas.yaml")

    # API v1 / DynamoDB
    JWT_SECRET: str = os.getenv("JWT_SECRET", "ttyd-dev-secret-change-in-production")
    JWT_ACCESS_EXPIRE_SECONDS: int = int(os.getenv("JWT_ACCESS_EXPIRE_SECONDS", "3600"))
    JWT_REFRESH_EXPIRE_SECONDS: int = int(os.getenv("JWT_REFRESH_EXPIRE_SECONDS", "604800"))
    DYNAMODB_ENDPOINT: str | None = os.getenv("DYNAMODB_ENDPOINT") or None
    DYNAMODB_TABLE_PREFIX: str = os.getenv("DYNAMODB_TABLE_PREFIX", "ttyd")
    ASSISTANT_DISPLAY_NAME: str = os.getenv("ASSISTANT_DISPLAY_NAME", "RecordAI")
    CHAT_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("CHAT_RATE_LIMIT_PER_MINUTE", "30"))
    GUARDRAILS_ENABLED: bool = os.getenv("GUARDRAILS_ENABLED", "true").lower() == "true"
    # Em dev/local, API retorna causa do erro LLM (nunca habilitar em prod)
    APP_EXPOSE_LLM_ERRORS: bool = os.getenv(
        "APP_EXPOSE_LLM_ERRORS",
        "true" if ENV_NAME in ("dev", "local") else "false",
    ).lower() == "true"

    # Microsoft Entra (OAuth/MSAL legado) — variáveis preservadas, fluxo paralelo ao SAML
    ENTRA_TENANT_ID: str = os.getenv("ENTRA_TENANT_ID") or os.getenv("APP_AUTH_MICROSOFT_TENANT_ID", "")
    ENTRA_CLIENT_ID: str = os.getenv("ENTRA_CLIENT_ID") or os.getenv("APP_AUTH_MICROSOFT_CLIENT_ID", "")
    ENTRA_CLIENT_SECRET: str = os.getenv("ENTRA_CLIENT_SECRET") or os.getenv(
        "APP_AUTH_MICROSOFT_CLIENT_SECRET", ""
    )
    ENTRA_REDIRECT_URI: str = os.getenv(
        "ENTRA_REDIRECT_URI",
        os.getenv("APP_AUTH_MICROSOFT_REDIRECT_URI", "http://localhost:8000/v1/auth/callback"),
    )

    # SAML 2.0 — Record / Microsoft Entra ID como IdP, TTYD como SP
    APP_AUTH_SAML_ENABLED: bool = os.getenv("APP_AUTH_SAML_ENABLED", "false").lower() == "true"
    # Simula login Microsoft sem Entra (somente DEV_OFFLINE=true)
    APP_AUTH_SAML_DEV_MOCK: bool = os.getenv("APP_AUTH_SAML_DEV_MOCK", "false").lower() == "true"
    APP_AUTH_SAML_MOCK_EMAIL: str = os.getenv(
        "APP_AUTH_SAML_MOCK_EMAIL", "diego.silva@record.com.br"
    )
    APP_AUTH_SAML_MOCK_DISPLAY_NAME: str = os.getenv(
        "APP_AUTH_SAML_MOCK_DISPLAY_NAME", "Diego Silva (SSO mock)"
    )
    APP_AUTH_SAML_SP_ENTITY_ID: str = os.getenv(
        "APP_AUTH_SAML_SP_ENTITY_ID",
        "http://localhost:8000/v1/auth/saml/metadata",
    )
    APP_AUTH_SAML_SP_ACS_URL: str = os.getenv(
        "APP_AUTH_SAML_SP_ACS_URL",
        "http://localhost:8000/v1/auth/saml/callback",
    )
    APP_AUTH_SAML_SP_SLO_URL: str = os.getenv("APP_AUTH_SAML_SP_SLO_URL", "")
    APP_AUTH_SAML_IDP_ENTITY_ID: str = os.getenv("APP_AUTH_SAML_IDP_ENTITY_ID", "")
    APP_AUTH_SAML_IDP_SSO_URL: str = os.getenv("APP_AUTH_SAML_IDP_SSO_URL", "")
    APP_AUTH_SAML_IDP_CERT: str = os.getenv("APP_AUTH_SAML_IDP_CERT", "")
    APP_AUTH_SAML_AUTO_PROVISION: bool = (
        os.getenv("APP_AUTH_SAML_AUTO_PROVISION", "true").lower() == "true"
    )
    APP_AUTH_SAML_DEFAULT_ROLE: str = os.getenv("APP_AUTH_SAML_DEFAULT_ROLE", "ttyd:user")
    APP_AUTH_SAML_NAME_ID_FORMAT: str = os.getenv(
        "APP_AUTH_SAML_NAME_ID_FORMAT",
        "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
    )
    APP_AUTH_SAML_FRONTEND_LOGIN_URL: str = os.getenv(
        "APP_AUTH_SAML_FRONTEND_LOGIN_URL",
        "http://localhost:4200/login",
    )


settings = Settings()
