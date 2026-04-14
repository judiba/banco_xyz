from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.core.config import MOCK_DB_PATH

@lru_cache(maxsize=1)
def _load() -> list[dict]:
    return json.loads(Path(MOCK_DB_PATH).read_text(encoding="utf-8"))


def list_clients() -> list[dict]:
    records = _load()
    return sorted(records, key=lambda item: item["id_pessoa"])


def get_client(client_id: str) -> dict:
    for client in _load():
        if client["id_pessoa"] == client_id:
            return client
    raise KeyError(f"Cliente {client_id} não encontrado")
