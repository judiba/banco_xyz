from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.api.v1.errors import ApiException
from backend.infrastructure.persistence.models import UserRecord
from backend.services.auth_service import decode_access_token, get_current_user

security = HTTPBearer(auto_error=False)


async def get_request_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> UserRecord:
    if not credentials or not credentials.credentials:
        raise ApiException(401, "AUTH_TOKEN_EXPIRED", "Token ausente.")
    payload = decode_access_token(credentials.credentials)
    return get_current_user(payload["sub"])


CurrentUser = Annotated[UserRecord, Depends(get_request_user)]


def pagination_params(
    page: int = 1,
    pageSize: int = 50,
    sort: str = "lastUpdatedAt",
    order: str = "desc",
) -> dict:
    page = max(1, page)
    page_size = min(100, max(1, pageSize))
    return {"page": page, "page_size": page_size, "sort": sort, "order": order}


def optional_bearer(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> str | None:
    return credentials.credentials if credentials else None
