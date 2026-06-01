from __future__ import annotations

import asyncio
import importlib
import json
import logging
import time
from collections import defaultdict
from typing import AsyncIterator

from backend.api.v1.errors import ApiException
from backend.api.v1.schemas.common import ErrorDetail
from backend.api.v1.utils import now_ms, to_conversation_summary, to_message_out
from backend.app_config.settings import settings
from backend.infrastructure.persistence.factory import get_store
from backend.infrastructure.persistence.models import ConversationRecord
from backend.runtime.orchestrator import Orchestrator
from backend.services.response_guardrails import apply_guardrails
from backend.services.response_presentation import present_assistant_response

logger = logging.getLogger(__name__)

_rate_buckets: dict[str, list[float]] = defaultdict(list)
_orchestrator = Orchestrator()


def _raise_llm_unavailable(exc: BaseException) -> None:
    """Registra stack trace nos logs e opcionalmente expõe causa na resposta API."""
    logger.exception("Falha ao invocar LLM/RAG (org_id=%s)", exc)
    message = "O assistente está temporariamente indisponível."
    details: list[ErrorDetail] = []
    if settings.APP_EXPOSE_LLM_ERRORS:
        cause = f"{type(exc).__name__}: {exc}"
        message = f"{message} Detalhe: {cause}"
        details = [ErrorDetail(field="cause", message=cause)]
    raise ApiException(503, "LLM_UNAVAILABLE", message, details=details) from exc


def _viewer_roles(user_id: str) -> list[str]:
    user = get_store().get_user(user_id)
    return list(user.roles) if user else ["ttyd:user"]


def _check_rate_limit(user_id: str) -> None:
    now = time.time()
    window = _rate_buckets[user_id]
    window[:] = [t for t in window if now - t < 60]
    if len(window) >= settings.CHAT_RATE_LIMIT_PER_MINUTE:
        raise ApiException(
            429,
            "CHAT_RATE_LIMIT",
            "Muitas perguntas em pouco tempo. Aguarde alguns segundos.",
            details=[ErrorDetail(field="retryAfter", message="30")],
        )
    window.append(now)


async def _generate_assistant_content(prompt: str, org_id: str) -> str:
    if settings.DEV_OFFLINE:
        return (
            f"Entendi. Segue um resumo da análise e próximos passos.\n\n"
            f"**Pergunta:** {prompt}\n\n"
            f"**Destaques**\n"
            f"- Share médio: 23.5 no horário das 20h\n"
            f"- Audiência pico: 1.2 milhões entre 21:15 e 21:45\n"
            f"- Crescimento vs. semana anterior: 0.08\n\n"
            f"**Sugestões**\n"
            f"- Validar mudança de grade\n"
            f"- Segmentar por praça"
        )
    try:
        module = importlib.import_module("backend.agents.orchestrator.orchestrator")
        orchestrator = module.get_orchestrator()
        response = await orchestrator.run(question=prompt)

        text = (
            str(response.get("text") or response) if isinstance(response, dict) else str(response)
        )
        if text.startswith("Erro:") or "Agente RAG não disponível" in text:
            raise RuntimeError(text)
        return text

    except ApiException:
        raise
    except Exception as exc:
        _raise_llm_unavailable(exc)
        raise


def _finalize_assistant_content(user_question: str, raw: str) -> str:
    """Pós-LLM: guardrails → texto validado (ou fallback)."""
    return apply_guardrails(user_question, raw).content


def _maybe_update_title(conv: ConversationRecord, content: str) -> None:
    if conv.title == "Novo chat" and len(content) > 10:
        conv.title = content[:60] + ("..." if len(content) > 60 else "")


async def send_message_async(
    user_id: str,
    conversation_id: str,
    content: str,
    *,
    org_id: str | None = None,
) -> dict:
    _check_rate_limit(user_id)
    store = get_store()
    conv = store.get_conversation(user_id, conversation_id)
    if not conv:
        raise ApiException(404, "CONVERSATION_NOT_FOUND", "Conversa não encontrada.")

    text = content.strip()
    if not text:
        raise ApiException(
            422,
            "VALIDATION_ERROR",
            "Dados inválidos.",
            details=[ErrorDetail(field="content", message="Informe uma pergunta.")],
        )

    user_msg = store.create_message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=text,
    )
    _maybe_update_title(conv, text)
    conv.last_updated_at = now_ms()

    user = store.get_user(user_id)
    tenant = org_id or (user.tenant_id if user else None) or "dev-org"
    roles = _viewer_roles(user_id)
    raw_llm = await _generate_assistant_content(text, tenant)
    raw_assistant_text = _finalize_assistant_content(text, raw_llm)

    assistant_msg = store.create_message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
        content=raw_assistant_text,
    )
    conv.last_updated_at = now_ms()
    store.update_conversation(conv)

    return {
        "conversation": to_conversation_summary(conv.to_dict()),
        "userMessage": to_message_out(user_msg.to_dict(), viewer_roles=roles),
        "assistantMessage": to_message_out(assistant_msg.to_dict(), viewer_roles=roles),
    }


async def stream_message_events(
    user_id: str,
    conversation_id: str,
    content: str,
    *,
    org_id: str | None = None,
) -> AsyncIterator[str]:
    _check_rate_limit(user_id)
    store = get_store()
    conv = store.get_conversation(user_id, conversation_id)
    if not conv:
        raise ApiException(404, "CONVERSATION_NOT_FOUND", "Conversa não encontrada.")

    text = content.strip()
    if not text:
        raise ApiException(
            422,
            "VALIDATION_ERROR",
            "Dados inválidos.",
            details=[ErrorDetail(field="content", message="Informe uma pergunta.")],
        )

    user_msg = store.create_message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=text,
    )
    roles = _viewer_roles(user_id)
    yield _sse("user_message", {"message": to_message_out(user_msg.to_dict(), viewer_roles=roles)})

    assistant_msg = store.create_message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
        content="",
        status="pending",
    )
    yield _sse(
        "assistant_start",
        {"messageId": assistant_msg.id, "conversationId": conversation_id},
    )

    raw_content = ""
    if settings.DEV_OFFLINE:
        async for token in _orchestrator.stream(text):
            raw_content += token
        raw_content = _finalize_assistant_content(text, raw_content)
    else:
        tenant = org_id
        try:
            user = store.get_user(user_id)
            tenant = tenant or (user.tenant_id if user else None) or "dev-org"
            raw_llm = await _generate_assistant_content(text, tenant)
            raw_content = _finalize_assistant_content(text, raw_llm)
        except ApiException as exc:
            yield _sse(
                "error",
                {
                    "code": exc.code,
                    "message": exc.message,
                    "details": [d.model_dump() for d in exc.details],
                },
            )
            return

    display_content = present_assistant_response(raw_content, roles)
    chunk_size = 40
    for i in range(0, len(display_content), chunk_size):
        yield _sse(
            "assistant_delta",
            {"messageId": assistant_msg.id, "delta": display_content[i : i + chunk_size]},
        )
        await asyncio.sleep(0.02)

    store.update_message_content(assistant_msg, raw_content)
    _maybe_update_title(conv, text)
    conv.last_updated_at = now_ms()
    store.update_conversation(conv)

    assistant_msg.content = raw_content
    yield _sse(
        "assistant_done",
        {"message": to_message_out(assistant_msg.to_dict(), viewer_roles=roles)},
    )
    yield _sse(
        "conversation_updated",
        {"conversation": to_conversation_summary(conv.to_dict())},
    )


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def regenerate_message(
    user_id: str,
    conversation_id: str,
    message_id: str,
    instruction: str | None = None,
) -> dict:
    _check_rate_limit(user_id)
    store = get_store()
    conv = store.get_conversation(user_id, conversation_id)
    if not conv:
        raise ApiException(404, "CONVERSATION_NOT_FOUND", "Conversa não encontrada.")

    msg = store.get_message(message_id)
    if not msg or msg.conversation_id != conversation_id or msg.role != "assistant":
        raise ApiException(404, "CONVERSATION_NOT_FOUND", "Mensagem não encontrada.")

    last_user = None
    for m in reversed(store.list_messages(conversation_id)):
        if m.role == "user":
            last_user = m.content
            break
    prompt = last_user or ""
    if instruction:
        prompt = f"{prompt}\n\nInstrução adicional: {instruction}"

    user = store.get_user(user_id)
    tenant = (user.tenant_id if user else None) or "dev-org"
    roles = _viewer_roles(user_id)
    raw_llm = await _generate_assistant_content(prompt, tenant)
    raw_content = _finalize_assistant_content(prompt, raw_llm)
    store.update_message_content(msg, raw_content)
    conv.last_updated_at = now_ms()
    store.update_conversation(conv)

    return {
        "message": to_message_out(msg.to_dict(), viewer_roles=roles),
        "conversation": to_conversation_summary(conv.to_dict()),
    }
