from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from backend.api.v1.schemas.conversation import ConversationSummary


class ChatMessage(BaseModel):
    id: str
    conversationId: str
    role: Literal["user", "assistant"]
    content: str
    createdAt: int
    status: str | None = "completed"
    feedback: Literal["like", "dislike"] | None = None


class SendMessageRequest(BaseModel):
    content: str


class SendMessageResponse(BaseModel):
    conversation: ConversationSummary
    userMessage: ChatMessage
    assistantMessage: ChatMessage


class RegenerateRequest(BaseModel):
    instruction: str | None = None


class RegenerateResponse(BaseModel):
    message: ChatMessage
    conversation: ConversationSummary


class FeedbackRequest(BaseModel):
    feedback: Literal["like", "dislike"] | None


class FeedbackResponse(BaseModel):
    messageId: str
    feedback: Literal["like", "dislike"] | None
    updatedAt: int
