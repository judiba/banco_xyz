from __future__ import annotations

from pydantic import BaseModel


class FolderOut(BaseModel):
    id: str
    name: str
    slug: str
    createdAt: int | None = None
    updatedAt: int | None = None
    conversationsCount: int | None = None


class FoldersListResponse(BaseModel):
    data: list[FolderOut]


class CreateFolderRequest(BaseModel):
    name: str


class PatchFolderRequest(BaseModel):
    name: str


class DeleteFolderResponse(BaseModel):
    deletedFolderId: str
    deletedConversationsCount: int
