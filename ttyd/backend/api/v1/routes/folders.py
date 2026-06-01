from __future__ import annotations

from fastapi import APIRouter, Query, Response

from backend.api.v1.deps import CurrentUser
from backend.api.v1.errors import ApiException
from backend.api.v1.schemas.common import ErrorDetail
from backend.api.v1.schemas.folder import (
    CreateFolderRequest,
    DeleteFolderResponse,
    FolderOut,
    FoldersListResponse,
    PatchFolderRequest,
)
from backend.api.v1.utils import matches_search, to_folder_out
from backend.infrastructure.persistence.factory import get_store

router = APIRouter(prefix="/folders", tags=["folders"])


@router.get("", response_model=FoldersListResponse)
def list_folders(
    user: CurrentUser,
    q: str | None = Query(default=None),
    sort: str = "name",
    order: str = "asc",
):
    _ = sort, order
    store = get_store()
    folders = store.list_folders(user.id)
    if q:
        folders = [f for f in folders if matches_search(f.name, q)]
    folders.sort(key=lambda f: f.name.lower())
    return FoldersListResponse(
        data=[
            FolderOut(
                **to_folder_out(
                    f.to_dict(),
                    store.count_conversations_in_folder(user.id, f.id),
                )
            )
            for f in folders
        ]
    )


@router.get("/by-slug/{slug}", response_model=FolderOut)
def get_folder_by_slug(user: CurrentUser, slug: str):
    store = get_store()
    folder = store.get_folder_by_slug(user.id, slug)
    if not folder:
        raise ApiException(404, "FOLDER_NOT_FOUND", "Pasta não encontrada.")
    return FolderOut(
        **to_folder_out(
            folder.to_dict(),
            store.count_conversations_in_folder(user.id, folder.id),
        )
    )


@router.get("/{folder_id}", response_model=FolderOut)
def get_folder(user: CurrentUser, folder_id: str):
    store = get_store()
    folder = store.get_folder(user.id, folder_id)
    if not folder:
        folder = store.get_folder_by_slug(user.id, folder_id)
    if not folder:
        raise ApiException(404, "FOLDER_NOT_FOUND", "Pasta não encontrada.")
    return FolderOut(
        **to_folder_out(
            folder.to_dict(),
            store.count_conversations_in_folder(user.id, folder.id),
        )
    )


@router.post("", response_model=FolderOut, status_code=201)
def create_folder(user: CurrentUser, payload: CreateFolderRequest):
    name = payload.name.strip()
    if not name:
        raise ApiException(
            422,
            "VALIDATION_ERROR",
            "Dados inválidos.",
            details=[ErrorDetail(field="name", message="Informe o nome da pasta.")],
        )
    store = get_store()
    if store.folder_name_exists(user.id, name):
        raise ApiException(
            409,
            "FOLDER_DUPLICATE_NAME",
            "Já existe uma pasta com este nome.",
            details=[ErrorDetail(field="name", message="Nome duplicado.")],
        )
    folder = store.create_folder(user.id, name)
    return FolderOut(**to_folder_out(folder.to_dict(), 0))


@router.patch("/{folder_id}", response_model=FolderOut)
def patch_folder(user: CurrentUser, folder_id: str, payload: PatchFolderRequest):
    name = payload.name.strip()
    if not name:
        raise ApiException(
            422,
            "VALIDATION_ERROR",
            "Dados inválidos.",
            details=[ErrorDetail(field="name", message="Informe o nome da pasta.")],
        )
    store = get_store()
    folder = store.get_folder(user.id, folder_id)
    if not folder:
        raise ApiException(404, "FOLDER_NOT_FOUND", "Pasta não encontrada.")
    if store.folder_name_exists(user.id, name, exclude_id=folder_id):
        raise ApiException(
            409,
            "FOLDER_DUPLICATE_NAME",
            "Já existe uma pasta com este nome.",
            details=[ErrorDetail(field="name", message="Nome duplicado.")],
        )
    folder = store.update_folder(folder, name)
    return FolderOut(
        **to_folder_out(
            folder.to_dict(),
            store.count_conversations_in_folder(user.id, folder.id),
        )
    )


@router.delete("/{folder_id}")
def delete_folder(
    user: CurrentUser,
    folder_id: str,
    cascade: bool = Query(default=True),
):
    store = get_store()
    folder = store.get_folder(user.id, folder_id)
    if not folder:
        raise ApiException(404, "FOLDER_NOT_FOUND", "Pasta não encontrada.")
    deleted_count = store.delete_folder(user.id, folder_id, cascade=cascade)
    if cascade:
        return DeleteFolderResponse(
            deletedFolderId=folder_id,
            deletedConversationsCount=deleted_count,
        )
    return Response(status_code=204)
