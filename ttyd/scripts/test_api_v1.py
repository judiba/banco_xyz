#!/usr/bin/env python3
"""
Script de teste de integração rápido para a API v1.
Substitui o script de shell legado mantendo a elegância e os padrões do projeto.
Requer que o backend esteja em execução (http://localhost:8000).
"""

import os
import sys
import json
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/v1")


def print_title(title: str) -> None:
    print(f"\n=== {title} ===")


def main() -> None:
    print("🚀 Iniciando Teste de Integração da API v1...")

    # 1. Health check (GET /health)
    print_title("Health Check")
    health_url = BASE_URL.replace("/v1", "/health")
    try:
        r_health = requests.get(health_url, timeout=5)
        r_health.raise_for_status()
        print(json.dumps(r_health.json(), indent=2, ensure_ascii=False))
    except requests.exceptions.RequestException as e:
        print(f"❌ Falha ao conectar no Health Check ({health_url}): {e}")
        sys.exit(1)

    # 2. Login (POST /v1/auth/login)
    print_title("Autenticação (Login)")
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {"username": "adminrecord", "password": "record123"}
    try:
        r_login = requests.post(login_url, json=login_payload, timeout=5)
        r_login.raise_for_status()
        login_data = r_login.json()
        token = login_data.get("tokens", {}).get("accessToken")
        if not token:
            print("❌ Erro: accessToken não encontrado na resposta de login.")
            sys.exit(1)
        print(f"✅ Token obtido com sucesso! ({len(token)} caracteres)")
    except requests.exceptions.RequestException as e:
        print(f"❌ Falha na autenticação em {login_url}: {e}")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {token}"}

    # 3. Bootstrap Session (GET /v1/session/bootstrap)
    print_title("Bootstrap de Sessão")
    bootstrap_url = f"{BASE_URL}/session/bootstrap"
    try:
        r_boot = requests.get(bootstrap_url, headers=headers, timeout=5)
        r_boot.raise_for_status()
        # Mostra as primeiras 40 linhas da resposta formatada
        boot_formatted = json.dumps(r_boot.json(), indent=2, ensure_ascii=False)
        lines = boot_formatted.splitlines()
        print("\n".join(lines[:40]))
        if len(lines) > 40:
            print("... (conteúdo truncado para visualização)")
    except requests.exceptions.RequestException as e:
        print(f"❌ Falha no bootstrap de sessão em {bootstrap_url}: {e}")
        sys.exit(1)

    # 4. Nova conversa com mensagem (POST /v1/conversations/with-message)
    print_title("Nova Conversa com Mensagem")
    msg_url = f"{BASE_URL}/conversations/with-message"
    msg_payload = {"content": "Teste script automatizado"}
    try:
        r_msg = requests.post(msg_url, headers=headers, json=msg_payload, timeout=10)
        r_msg.raise_for_status()
        msg_formatted = json.dumps(r_msg.json(), indent=2, ensure_ascii=False)
        lines = msg_formatted.splitlines()
        print("\n".join(lines[:25]))
        if len(lines) > 25:
            print("... (conteúdo truncado para visualização)")
    except requests.exceptions.RequestException as e:
        print(f"❌ Falha ao enviar mensagem em {msg_url}: {e}")
        sys.exit(1)

    print("\n✅ OK — todos os passos concluídos com sucesso! 🚀\n")


if __name__ == "__main__":
    main()
