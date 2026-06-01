from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Query
from fastapi.responses import Response

from backend.api.v1.deps import CurrentUser
from backend.api.v1.errors import ApiException
from backend.api.v1.utils import slugify
from backend.app_config.settings import settings
from backend.infrastructure.persistence.factory import get_store
from backend.services.response_presentation import present_assistant_response

router = APIRouter(prefix="/conversations", tags=["export"])


def _build_export_txt(
    user_name: str,
    conv_title: str,
    conv_description: str | None,
    messages: list,
    viewer_roles: list[str],
) -> str:
    exported_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    lines = [
        "Exportação de conversa",
        "====================",
        f"Usuário: {user_name}",
        f"Conversa: {conv_title}",
        f"Descrição: {conv_description or '-'}",
        f"Data de exportação: {exported_at}",
        "",
        "Mensagens",
        "--------",
    ]
    for msg in messages:
        role_label = "Usuário" if msg.role == "user" else settings.ASSISTANT_DISPLAY_NAME
        ts = datetime.fromtimestamp(msg.created_at / 1000).strftime("%d/%m/%Y %H:%M:%S")
        body = msg.content
        if msg.role == "assistant":
            body = present_assistant_response(body, viewer_roles)
        lines.extend(["", f"[{role_label}] {ts}", body])
    return "\n".join(lines)


@router.get("/{conversation_id}/export")
def export_conversation(
    user: CurrentUser,
    conversation_id: str,
    format: str = Query(default="txt", alias="format"),
):
    if format not in ("txt", "pdf"):
        raise ApiException(400, "VALIDATION_ERROR", "Formato inválido. Use txt ou pdf.")

    store = get_store()
    conv = store.get_conversation(user.id, conversation_id)
    if not conv:
        raise ApiException(404, "CONVERSATION_NOT_FOUND", "Conversa não encontrada.")

    messages = store.list_messages(conversation_id)
    slug = slugify(conv.title)[:40]
    date_str = datetime.now().strftime("%Y-%m-%d")

    if format == "txt":
        body = _build_export_txt(
            user.display_name,
            conv.title,
            conv.description,
            messages,
            user.roles,
        )
        filename = f"{slug}-{date_str}.txt"
        return Response(
            content=body.encode("utf-8"),
            media_type="text/plain; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )

    raise ApiException(
        501,
        "NOT_IMPLEMENTED",
        "Exportação PDF ainda não implementada. Use format=txt.",
    )
