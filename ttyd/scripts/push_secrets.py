#!/usr/bin/env python3
"""
Script auxiliar: preenche o AWS Secrets Manager com os valores do .env.local.

Uso:
  poetry run python scripts/push_secrets.py --env local

O script lê o arquivo security/.env.{env}, filtra apenas as chaves sensíveis
e faz upload para o Secrets Manager.

⚠️  Nunca exibe os valores em tela ou logs.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Chaves a sincronizar com o Secrets Manager
SENSITIVE_KEYS = {
    "REDSHIFT_LAMBDA_ARN",
    "REDSHIFT_LAKE_BIG_DATA_ARN",
    "REDSHIFT_LAKE_ID_UNICO_ARN",
    "RAG_BUCKET",
    "GLUE_DATABASE",
}

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def parse_env_file(path: Path) -> dict:
    """Lê um arquivo .env e retorna as variáveis como dict."""
    env_vars = {}
    if not path.exists():
        print(f"❌ Arquivo não encontrado: {path}")
        sys.exit(1)
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env_vars[key.strip()] = value.strip().strip('"').strip("'")
    return env_vars


def push_secrets(env: str, dry_run: bool = False) -> None:
    env_file = PROJECT_ROOT / "security" / f".env.{env}"
    secret_name = f"ttyd/{env}/config"

    print(f"\n🔐 Push de secrets para '{secret_name}' [{env}]")
    print(f"📄 Origem: {env_file}\n")

    all_vars = parse_env_file(env_file)

    # Filtra apenas as chaves sensíveis com valor preenchido
    secrets = {
        k: v
        for k, v in all_vars.items()
        if k in SENSITIVE_KEYS and v and v not in ("", "your-value-here")
    }

    if not secrets:
        print("⚠️  Nenhuma chave sensível preenchida encontrada no .env. Verifique o arquivo.")
        return

    print(f"📦 {len(secrets)} chave(s) a sincronizar:")
    for key in sorted(secrets.keys()):
        print(f"   ✓ {key} = {'*' * 8}")  # nunca exibe o valor

    if dry_run:
        print("\n🧪 Dry-run: nenhuma chamada AWS realizada.")
        return

    # Confirma antes de enviar
    confirm = input(f"\n⚠️  Confirma o push para '{secret_name}'? (s/N) ")
    if confirm.lower() not in ("s", "sim", "y", "yes"):
        print("❌ Cancelado.")
        return

    import boto3

    client = boto3.client("secretsmanager", region_name=os.getenv("AWS_REGION", "us-east-1"))

    try:
        client.put_secret_value(
            SecretId=secret_name,
            SecretString=json.dumps(secrets),
        )
        print(f"\n✅ Secrets atualizados com sucesso em '{secret_name}'.")
    except client.exceptions.ResourceNotFoundException:
        print(f"❌ Secret '{secret_name}' não encontrado. Execute 'make tf-up' primeiro.")
        sys.exit(1)
    except Exception as exc:
        print(f"❌ Falha ao atualizar secrets: {exc}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Push de secrets para AWS Secrets Manager")
    parser.add_argument("--env", required=True, choices=["local"], help="Ambiente alvo: local")
    parser.add_argument("--dry-run", action="store_true", help="Valida sem fazer chamadas AWS")
    args = parser.parse_args()
    push_secrets(args.env, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
