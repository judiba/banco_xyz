from __future__ import annotations

from fastapi import APIRouter, Query, Response

from backend.api.v1.deps import CurrentUser, pagination_params
from backend.api.v1.errors import ApiException
from backend.api.v1.schemas.common import ErrorDetail, PaginatedResponse, build_pagination
from backend.api.v1.schemas.conversation import (
    ConversationSummary,
    CreateConversationRequest,
    PatchConversationRequest,
    WithMessageRequest,
    WithMessageResponse,
)
from backend.api.v1.schemas.message import ChatMessage
from backend.api.v1.utils import to_conversation_summary
from backend.infrastructure.persistence.factory import get_store
from backend.services import chat_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _parse_folder_filter(folderId: str | None) -> str | None | object:
    if folderId is None:
        return "__unset__"
    if folderId in ("null", "none", ""):
        return None
    return folderId


@router.get("", response_model=PaginatedResponse[ConversationSummary])
def list_conversations(
    user: CurrentUser,
    page: int = 1,
    pageSize: int = 50,
    sort: str = "lastUpdatedAt",
    order: str = "desc",
    folderId: str | None = Query(default=None),
    q: str | None = Query(default=None),
):
    _ = sort, order
    store = get_store()
    params = pagination_params(page=page, pageSize=pageSize)
    convs = store.list_conversations(
        user.id,
        folder_id=_parse_folder_filter(folderId),
        q=q,
    )
    total = len(convs)
    start = (params["page"] - 1) * params["page_size"]
    end = start + params["page_size"]
    return PaginatedResponse(
        data=[
            ConversationSummary(**to_conversation_summary(c.to_dict())) for c in convs[start:end]
        ],
        pagination=build_pagination(params["page"], params["page_size"], total),
    )


@router.post("", response_model=ConversationSummary, status_code=201)
def create_conversation(user: CurrentUser, payload: CreateConversationRequest):
    store = get_store()
    if payload.folderId:
        if not store.get_folder(user.id, payload.folderId):
            raise ApiException(404, "FOLDER_NOT_FOUND", "Pasta não encontrada.")
    conv = store.create_conversation(
        user.id,
        title=payload.title or "Novo chat",
        folder_id=payload.folderId,
    )
    return ConversationSummary(**to_conversation_summary(conv.to_dict()))


@router.post("/with-message", response_model=WithMessageResponse, status_code=201)
async def create_with_message(user: CurrentUser, payload: WithMessageRequest):
    store = get_store()
    if payload.folderId and not store.get_folder(user.id, payload.folderId):
        raise ApiException(404, "FOLDER_NOT_FOUND", "Pasta não encontrada.")

    text = payload.content.strip()
    if not text:
        raise ApiException(
            422,
            "VALIDATION_ERROR",
            "Dados inválidos.",
            details=[ErrorDetail(field="content", message="Informe uma pergunta.")],
        )

    conv = store.create_conversation(
        user.id,
        title="Novo chat",
        description=text,
        folder_id=payload.folderId,
    )
    result = await chat_service.send_message_async(user.id, conv.id, text)
    conv = store.get_conversation(user.id, conv.id)
    result["conversation"] = to_conversation_summary(conv.to_dict())
    if not conv.description:
        conv.description = text
        store.update_conversation(conv)
        result["conversation"]["description"] = text

    return WithMessageResponse(
        conversation=ConversationSummary(**result["conversation"]),
        userMessage=ChatMessage(**result["userMessage"]),
        assistantMessage=ChatMessage(**result["assistantMessage"]),
    )


@router.get("/{conversation_id}", response_model=ConversationSummary)
def get_conversation(user: CurrentUser, conversation_id: str):
    store = get_store()
    conv = store.get_conversation(user.id, conversation_id)
    if not conv:
        raise ApiException(404, "CONVERSATION_NOT_FOUND", "Conversa não encontrada.")
    return ConversationSummary(**to_conversation_summary(conv.to_dict()))


@router.patch("/{conversation_id}", response_model=ConversationSummary)
def patch_conversation(
    user: CurrentUser,
    conversation_id: str,
    payload: PatchConversationRequest,
):
    store = get_store()
    conv = store.get_conversation(user.id, conversation_id)
    if not conv:
        raise ApiException(404, "CONVERSATION_NOT_FOUND", "Conversa não encontrada.")

    updates = payload.model_dump(exclude_unset=True)
    if "title" in updates:
        title = (updates["title"] or "").strip()
        if not title:
            raise ApiException(
                422,
                "VALIDATION_ERROR",
                "Dados inválidos.",
                details=[ErrorDetail(field="title", message="Informe o nome da conversa.")],
            )
        conv.title = title

    if "folderId" in updates:
        folder_id = updates["folderId"]
        if folder_id and not store.get_folder(user.id, folder_id):
            raise ApiException(404, "FOLDER_NOT_FOUND", "Pasta não encontrada.")
        conv.folder_id = folder_id

    store.update_conversation(conv)
    return ConversationSummary(**to_conversation_summary(conv.to_dict()))


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(user: CurrentUser, conversation_id: str):
    store = get_store()
    if not store.delete_conversation(user.id, conversation_id):
        raise ApiException(404, "CONVERSATION_NOT_FOUND", "Conversa não encontrada.")
    return Response(status_code=204)
