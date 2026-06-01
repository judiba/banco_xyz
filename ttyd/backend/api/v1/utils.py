from __future__ import annotations

import re
import time
import unicodedata
import uuid
from typing import Any


def now_ms() -> int:
    return int(time.time() * 1000)


def new_id() -> str:
    return str(uuid.uuid4())


def slugify(name: str) -> str:
    normalized = unicodedata.normalize("NFD", name.strip().lower())
    without_accents = "".join(c for c in normalized if unicodedata.category(c) != "Mn")
    slug = re.sub(r"[^a-z0-9]+", "-", without_accents).strip("-")
    return slug or "pasta"


def normalize_search_query(q: str) -> str:
    normalized = unicodedata.normalize("NFD", q.strip().lower())
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


def matches_search(text: str | None, query: str) -> bool:
    if not text:
        return False
    return normalize_search_query(query) in normalize_search_query(text)


def to_conversation_summary(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item["id"],
        "title": item["title"],
        "description": item.get("description"),
        "lastUpdatedAt": item["lastUpdatedAt"],
        "folderId": item.get("folderId"),
    }


def to_folder_out(item: dict[str, Any], conversations_count: int | None = None) -> dict[str, Any]:
    out = {
        "id": item["id"],
        "name": item["name"],
        "slug": item["slug"],
        "createdAt": item.get("createdAt"),
        "updatedAt": item.get("updatedAt"),
    }
    if conversations_count is not None:
        out["conversationsCount"] = conversations_count
    return out


def to_message_out(
    item: dict[str, Any], *, viewer_roles: list[str] | None = None
) -> dict[str, Any]:
    from backend.services.response_presentation import present_assistant_response

    content = item["content"]
    if viewer_roles is not None and item.get("role") == "assistant":
        content = present_assistant_response(content, viewer_roles)

    return {
        "id": item["id"],
        "conversationId": item["conversationId"],
        "role": item["role"],
        "content": content,
        "createdAt": item["createdAt"],
        "status": item.get("status", "completed"),
        "feedback": item.get("feedback"),
    }


def to_user_out(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item["id"],
        "username": item["username"],
        "displayName": item["displayName"],
        "email": item.get("email"),
        "roles": item.get("roles", ["ttyd:user"]),
        "tenantId": item.get("tenantId"),
    }
