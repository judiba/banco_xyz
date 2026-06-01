from __future__ import annotations

from fastapi import APIRouter

from backend.api.v1.deps import CurrentUser
from backend.api.v1.errors import ApiException
from backend.api.v1.schemas.message import FeedbackRequest, FeedbackResponse
from backend.api.v1.utils import now_ms
from backend.infrastructure.persistence.factory import get_store

router = APIRouter(prefix="/messages", tags=["feedback"])


@router.put("/{message_id}/feedback", response_model=FeedbackResponse)
def set_feedback(user: CurrentUser, message_id: str, payload: FeedbackRequest):
    store = get_store()
    msg = store.get_message(message_id)
    if not msg or msg.user_id != user.id:
        raise ApiException(404, "CONVERSATION_NOT_FOUND", "Mensagem não encontrada.")
    if msg.role != "assistant":
        raise ApiException(
            422,
            "VALIDATION_ERROR",
            "Feedback só é permitido em mensagens do assistente.",
        )
    store.set_message_feedback(msg, payload.feedback)
    return FeedbackResponse(
        messageId=message_id,
        feedback=payload.feedback,
        updatedAt=now_ms(),
    )
