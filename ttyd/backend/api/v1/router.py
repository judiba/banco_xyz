from __future__ import annotations

from fastapi import APIRouter

from backend.api.v1.routes import (
    auth,
    conversations,
    export,
    feedback,
    folders,
    messages,
    saml,
    session,
    users,
)

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(auth.router)
api_v1_router.include_router(saml.router)
api_v1_router.include_router(users.router)
api_v1_router.include_router(session.router)
api_v1_router.include_router(conversations.router)
api_v1_router.include_router(folders.router)
api_v1_router.include_router(messages.router)
api_v1_router.include_router(feedback.router)
api_v1_router.include_router(export.router)
