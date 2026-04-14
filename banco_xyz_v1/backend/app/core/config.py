from __future__ import annotations

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]  # /app/backend
DATA_DIR = BASE_DIR / "data"
CORPUS_DIR = DATA_DIR / "corpus"
VECTOR_DIR = DATA_DIR / "vector_store"
REPORTS_DIR = DATA_DIR / "reports"
DELIVERIES_DIR = DATA_DIR / "deliveries"
RAW_DIR = DATA_DIR / "raw"
MOCK_DB_PATH = DATA_DIR / "mock_clients.json"

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)

WHATSAPP_PROVIDER = os.getenv("WHATSAPP_PROVIDER", "stub")
WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")

print(f"DATA_DIR: {DATA_DIR}")
print(f"CORPUS_DIR: {CORPUS_DIR}")
print(f"REPORTS_DIR: {REPORTS_DIR}")
print(f"MOCK_DB_PATH: {MOCK_DB_PATH}")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    reports_base_url: str = "http://localhost:8000/api/reports/file?path="
    sqlite_db_path: str = str(DATA_DIR / "app_state.db")

    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_api_version: str = "2025-01-01-preview"
    azure_openai_chat_deployment: str | None = None
    azure_openai_embeddings_deployment: str | None = None
    azure_openai_model: str = "gpt-4.1-mini"

    vector_index_name: str = "bank_docs"

settings = Settings()