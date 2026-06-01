from __future__ import annotations

from backend.app_config.settings import settings
from backend.infrastructure.persistence.dynamodb_store import DynamoDBStore
from backend.infrastructure.persistence.memory_store import MemoryStore, get_memory_store

_store = None


def get_store() -> MemoryStore | DynamoDBStore:
    global _store
    if _store is not None:
        return _store
    if settings.DEV_OFFLINE:
        _store = get_memory_store()
    else:
        try:
            _store = DynamoDBStore()
        except Exception:
            _store = get_memory_store()
    return _store
