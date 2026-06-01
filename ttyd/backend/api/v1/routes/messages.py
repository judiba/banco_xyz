from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.api.v1.deps import CurrentUser, pagination_params
from backend.api.v1.errors import ApiException
from backend.api.v1.schemas.common import PaginatedResponse, build_pagination
from backend.api.v1.schemas.message import (
    ChatMessage,
    RegenerateRequest,
    RegenerateResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from backend.api.v1.schemas.conversation import ConversationSummary
from backend.api.v1.utils import to_message_out
from backend.infrastructure.persistence.factory import get_store
from backend.services import chat_service

router = APIRouter(tags=["messages"])


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=PaginatedResponse[ChatMessage],
)
def list_messages(
    user: CurrentUser,
    conversation_id: str,
    page: int = 1,
    pageSize: int = 100,
    order: str = "asc",
):
    store = get_store()
    if not store.get_conversation(user.id, conversation_id):
        raise ApiException(404, "CONVERSATION_NOT_FOUND", "Conversa não encontrada.")

    params = pagination_params(page=page, pageSize=pageSize)
    msgs = store.list_messages(conversation_id)
    if order == "desc":
        msgs = list(reversed(msgs))
    total = len(msgs)
    start = (params["page"] - 1) * params["page_size"]
    end = start + params["page_size"]

    return PaginatedResponse(
        data=[
            ChatMessage(**to_message_out(m.to_dict(), viewer_roles=user.roles))
            for m in msgs[start:end]
        ],
        pagination=build_pagination(params["page"], params["page_size"], total),
    )


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=SendMessageResponse,
    status_code=201,
)
async def send_message(
    user: CurrentUser,
    conversation_id: str,
    payload: SendMessageRequest,
):
    result = await chat_service.send_message_async(
        user.id,
        conversation_id,
        payload.content,
        org_id=user.tenant_id,
    )
    return SendMessageResponse(
        conversation=ConversationSummary(**result["conversation"]),
        userMessage=ChatMessage(**result["userMessage"]),
        assistantMessage=ChatMessage(**result["assistantMessage"]),
    )


@router.post("/conversations/{conversation_id}/messages/stream")
async def stream_message(
    user: CurrentUser,
    conversation_id: str,
    payload: SendMessageRequest,
):
    async def event_generator():
        async for chunk in chat_service.stream_message_events(
            user.id,
            conversation_id,
            payload.content,
            org_id=user.tenant_id,
        ):
            yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post(
    "/conversations/{conversation_id}/messages/{message_id}/regenerate",
    response_model=RegenerateResponse,
)
async def regenerate(
    user: CurrentUser,
    conversation_id: str,
    message_id: str,
    payload: RegenerateRequest | None = None,
):
    instruction = payload.instruction if payload else None
    result = await chat_service.regenerate_message(
        user.id,
        conversation_id,
        message_id,
        instruction,
    )
    return RegenerateResponse(
        message=ChatMessage(**result["message"]),
        conversation=ConversationSummary(**result["conversation"]),
    )
