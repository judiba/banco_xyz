from __future__ import annotations

from fastapi import APIRouter

from backend.api.v1.deps import CurrentUser, pagination_params
from backend.api.v1.schemas.common import PaginatedResponse, build_pagination
from backend.api.v1.schemas.conversation import ConversationSummary
from backend.api.v1.schemas.folder import FolderOut, FoldersListResponse
from backend.api.v1.schemas.session import AssistantInfo, BootstrapResponse
from backend.api.v1.utils import to_conversation_summary, to_folder_out, to_user_out
from backend.app_config.settings import settings
from backend.infrastructure.persistence.factory import get_store

router = APIRouter(prefix="/session", tags=["session"])


@router.get("/bootstrap", response_model=BootstrapResponse)
def bootstrap(user: CurrentUser, page: int = 1, pageSize: int = 50):
    store = get_store()
    params = pagination_params(page=page, pageSize=pageSize)
    convs = store.list_conversations(user.id)
    total = len(convs)
    start = (params["page"] - 1) * params["page_size"]
    end = start + params["page_size"]
    page_items = convs[start:end]

    folders = store.list_folders(user.id)
    folders.sort(key=lambda f: f.name.lower())

    return BootstrapResponse(
        user=to_user_out(user.to_dict()),
        conversations=PaginatedResponse(
            data=[ConversationSummary(**to_conversation_summary(c.to_dict())) for c in page_items],
            pagination=build_pagination(params["page"], params["page_size"], total),
        ),
        folders=FoldersListResponse(
            data=[
                FolderOut(
                    **to_folder_out(
                        f.to_dict(),
                        store.count_conversations_in_folder(user.id, f.id),
                    )
                )
                for f in folders
            ]
        ),
        assistant=AssistantInfo(displayName=settings.ASSISTANT_DISPLAY_NAME),
    )
