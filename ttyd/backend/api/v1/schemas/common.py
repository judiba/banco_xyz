from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    pageSize: int
    totalItems: int
    totalPages: int
    hasNext: bool
    hasPrevious: bool


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    pagination: PaginationMeta


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)
    requestId: str


class ErrorEnvelope(BaseModel):
    error: ErrorBody


def build_pagination(page: int, page_size: int, total_items: int) -> PaginationMeta:
    total_pages = max(1, (total_items + page_size - 1) // page_size) if total_items else 1
    return PaginationMeta(
        page=page,
        pageSize=page_size,
        totalItems=total_items,
        totalPages=total_pages,
        hasNext=page < total_pages,
        hasPrevious=page > 1,
    )
