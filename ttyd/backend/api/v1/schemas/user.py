from __future__ import annotations

from pydantic import BaseModel


class UserOut(BaseModel):
    id: str
    username: str
    displayName: str
    email: str | None = None
    roles: list[str]
    tenantId: str | None = None
