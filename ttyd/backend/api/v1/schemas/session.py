from __future__ import annotations

from pydantic import BaseModel

from backend.api.v1.schemas.common import PaginatedResponse
from backend.api.v1.schemas.conversation import ConversationSummary
from backend.api.v1.schemas.folder import FoldersListResponse
from backend.api.v1.schemas.user import UserOut


class AssistantInfo(BaseModel):
    displayName: str


class BootstrapResponse(BaseModel):
    user: UserOut
    conversations: PaginatedResponse[ConversationSummary]
    folders: FoldersListResponse
    assistant: AssistantInfo
