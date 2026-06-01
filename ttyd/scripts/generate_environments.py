from __future__ import annotations

import argparse
from pathlib import Path
from typing import Final

ROOT = Path(__file__).resolve().parent.parent
SECURITY_DIR = ROOT / "security"

ENV_EXAMPLE_CANDIDATES = [
    ROOT / ".env.example",
    SECURITY_DIR / ".env.example",
]


def find_env_example() -> Path:
    for path in ENV_EXAMPLE_CANDIDATES:
        if path.exists():
            return path

    raise FileNotFoundError(
        "Arquivo base .env.example não encontrado. "
        "Coloque o arquivo em .env.example ou security/.env.example"
    )


ENV_DEFAULTS: Final[dict[str, dict[str, str]]] = {
    "dev": {
        "APP_ENV": "dev",
        "DEV_OFFLINE": "true",
        "AWS_REGION": "us-east-1",
        "AWS_PROFILE": "",
        "LLM_MODEL": "mock",
        "RAG_EMBED_MODEL_ID": "mock",
        "RAG_EMBED_DIM": "1536",
        "RAG_BUCKET": "ttyd-dev-mock",
        "RAG_KEY": "data/rag/dev/",
        "SQL_KEY": "data/sql/dev/",
        "REDSHIFT_WORKGROUP_NAME": "",
        "REDSHIFT_ENDPOINT": "",
        "REDSHIFT_PORT": "5439",
        "REDSHIFT_DATABASE": "dev",
        "REDSHIFT_USER": "",
        "REDSHIFT_HOST": "",
        "REDSHIFT_DB": "dev",
        "CLUSTER_ID": "",
        "REDSHIFT_LAMBDA_ARN": "",
        "USE_IAM_AUTH": "false",
        "USE_SERVERLESS": "false",
        "YAML_PATH_TABLES": "backend/app_config/desc_tables.yaml",
        "YAML_PATH_COL": "backend/app_config/desc_colunas.yaml",
        "JWT_SECRET": "ttyd-dev-secret-change-in-production",
        "DYNAMODB_TABLE_PREFIX": "ttyd",
        "ASSISTANT_DISPLAY_NAME": "RecordAI",
        "APP_AUTH_SAML_ENABLED": "false",
        "APP_AUTH_SAML_DEV_MOCK": "false",
        "APP_AUTH_SAML_MOCK_EMAIL": "diego.silva@record.com.br",
        "APP_AUTH_SAML_MOCK_DISPLAY_NAME": "Diego Silva (SSO mock)",
        "APP_AUTH_SAML_SP_ENTITY_ID": "http://localhost:8000/v1/auth/saml/metadata",
        "APP_AUTH_SAML_SP_ACS_URL": "http://localhost:8000/v1/auth/saml/callback",
        "APP_AUTH_SAML_AUTO_PROVISION": "true",
        "APP_AUTH_SAML_DEFAULT_ROLE": "ttyd:user",
        "APP_AUTH_SAML_FRONTEND_LOGIN_URL": "http://localhost:4200/login",
        "ENTRA_TENANT_ID": "mock-tenant-id",
        "ENTRA_CLIENT_ID": "mock-client-id",
        "APP_AUTH_MICROSOFT_TENANT_ID": "mock-tenant-id",
        "APP_AUTH_MICROSOFT_CLIENT_ID": "mock-client-id",
        # Customizações solicitadas: Dev offline sem AWS e Mock local ativo
        "AWS_OFFLINE": "true",
        "USE_AWS_MOCK": "true",
        "USE_AGENT_CORE": "false",
    },
    "local": {
        "APP_ENV": "local",
        "DEV_OFFLINE": "false",
        "JWT_SECRET": "ttyd-local-secret-change-in-production",
        "DYNAMODB_TABLE_PREFIX": "ttyd",
        "ASSISTANT_DISPLAY_NAME": "RecordAI",
        "GUARDRAILS_ENABLED": "true",
        "AWS_REGION": "us-east-1",
        "AWS_PROFILE": "default",
        "LLM_MODEL": "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "RAG_EMBED_MODEL_ID": "amazon.titan-embed-text-v2:0",
        "RAG_EMBED_DIM": "1024",
        "RAG_BUCKET": "ttyd-local-rag",
        "RAG_KEY": "rag/",
        "SQL_KEY": "sql/",
        "REDSHIFT_WORKGROUP_NAME": "ttyd-local",
        "REDSHIFT_ENDPOINT": "",
        "REDSHIFT_PORT": "5439",
        "REDSHIFT_DATABASE": "dev",
        "REDSHIFT_USER": "",
        "REDSHIFT_HOST": "",
        "REDSHIFT_DB": "dev",
        "CLUSTER_ID": "",
        "REDSHIFT_LAMBDA_ARN": "",
        "USE_IAM_AUTH": "true",
        "USE_SERVERLESS": "true",
        "YAML_PATH_TABLES": "backend/app_config/desc_tables.yaml",
        "YAML_PATH_COL": "backend/app_config/desc_colunas.yaml",
        "APP_AUTH_SAML_ENABLED": "false",
        "APP_AUTH_SAML_SP_ENTITY_ID": "http://localhost:8000/v1/auth/saml/metadata",
        "APP_AUTH_SAML_SP_ACS_URL": "http://localhost:8000/v1/auth/saml/callback",
        "APP_AUTH_SAML_FRONTEND_LOGIN_URL": "http://localhost:4200/login",
        "ENTRA_TENANT_ID": "mock-tenant-id",
        "ENTRA_CLIENT_ID": "mock-client-id",
        "AWS_EXTERNAL_ROLE_ARN": "arn:aws:iam::123456789012:role/ttyd-external-access",
        # Customizações solicitadas: Desenvolvimento conectado com AWS Real
        "AWS_OFFLINE": "false",
        "USE_AWS_MOCK": "false",
        "USE_AGENT_CORE": "false",
    },
    "prod": {
        "APP_ENV": "prod",
        "DEV_OFFLINE": "false",
        "AWS_REGION": "us-east-1",
        "AWS_PROFILE": "",
        "LLM_MODEL": "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "RAG_EMBED_MODEL_ID": "amazon.titan-embed-text-v2:0",
        "RAG_EMBED_DIM": "1024",
        "RAG_BUCKET": "",
        "RAG_KEY": "rag/",
        "SQL_KEY": "sql/",
        "REDSHIFT_WORKGROUP_NAME": "",
        "REDSHIFT_ENDPOINT": "",
        "REDSHIFT_PORT": "5439",
        "REDSHIFT_DATABASE": "",
        "REDSHIFT_USER": "",
        "REDSHIFT_HOST": "",
        "REDSHIFT_DB": "",
        "CLUSTER_ID": "",
        "REDSHIFT_LAMBDA_ARN": "",
        "USE_IAM_AUTH": "true",
        "USE_SERVERLESS": "true",
        "YAML_PATH_TABLES": "backend/app_config/desc_tables.yaml",
        "YAML_PATH_COL": "backend/app_config/desc_colunas.yaml",
        "APP_AUTH_SAML_ENABLED": "true",
        "APP_AUTH_SAML_SP_ENTITY_ID": "https://record.ttyd.record.com/v1/auth/saml/metadata",
        "APP_AUTH_SAML_SP_ACS_URL": "https://record.ttyd.record.com/v1/auth/saml/callback",
        "APP_AUTH_SAML_FRONTEND_LOGIN_URL": "https://record.ttyd.record.com/login",
        "ENTRA_TENANT_ID": "",
        "ENTRA_CLIENT_ID": "",
        "AWS_EXTERNAL_ROLE_ARN": "",
        # Customizações solicitadas: Docker + Terraform usando AgentCore ativo
        "AWS_OFFLINE": "false",
        "USE_AWS_MOCK": "false",
        "USE_AGENT_CORE": "true",
        "CONTAINERIZED": "true",
    },
}


def _render_env(example_text: str, values: dict[str, str]) -> str:
    lines: list[str] = []

    for raw_line in example_text.splitlines():
        stripped = raw_line.strip()

        if not stripped or stripped.startswith("#") or "=" not in raw_line:
            lines.append(raw_line)
            continue

        key, _, current_value = raw_line.partition("=")
        key = key.strip()
        value = values.get(key, current_value.strip())
        lines.append(f"{key}={value}")

    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    # Garancia de isolamento de argumentos via CLI para o Makefile
    parser = argparse.ArgumentParser(description="Compilador de ambientes talktoyourdata")
    parser.add_argument(
        "--env",
        choices=["local", "dev", "prod", "all"],
        required=True,
        help="Defina qual escopo de ambiente gerar",
    )
    args = parser.parse_args()

    env_example = find_env_example()
    base_content = env_example.read_text(encoding="utf-8")

    # Determina se vai compilar um unico escopo ou a esteira inteira (all)
    target_envs = ENV_DEFAULTS.keys() if args.env == "all" else [args.env]

    for env_name in target_envs:
        values = ENV_DEFAULTS[env_name]
        target = SECURITY_DIR / f".env.{env_name}"
        target.write_text(_render_env(base_content, values), encoding="utf-8")
        print(f"Gerado: {target}")

    print(f"✅ Execução concluída para o escopo: {args.env.upper()}")
    print(f"✅ Ambientes gerados: {', '.join(target_envs)}")
    print(f"✅ Ambientes gerados em: {SECURITY_DIR}")
