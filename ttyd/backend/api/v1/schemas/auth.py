from __future__ import annotations

from pydantic import BaseModel

from backend.api.v1.schemas.user import UserOut


class AuthTokens(BaseModel):
    accessToken: str
    refreshToken: str
    expiresIn: int
    tokenType: str = "Bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    tokens: AuthTokens
    user: UserOut


class RefreshRequest(BaseModel):
    refreshToken: str


class RefreshResponse(BaseModel):
    tokens: AuthTokens


class LogoutRequest(BaseModel):
    refreshToken: str | None = None
