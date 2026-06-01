from __future__ import annotations

from pydantic import BaseModel, Field


class ConversationSummary(BaseModel):
    id: str
    title: str
    description: str | None
    lastUpdatedAt: int
    folderId: str | None


class CreateConversationRequest(BaseModel):
    title: str | None = "Novo chat"
    folderId: str | None = None


class PatchConversationRequest(BaseModel):
    title: str | None = None
    folderId: str | None = None


class WithMessageRequest(BaseModel):
    content: str
    folderId: str | None = None


class WithMessageResponse(BaseModel):
    conversation: ConversationSummary
    userMessage: "ChatMessage"
    assistantMessage: "ChatMessage"


from backend.api.v1.schemas.message import ChatMessage  # noqa: E402

WithMessageResponse.model_rebuild()
