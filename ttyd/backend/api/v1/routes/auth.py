from __future__ import annotations

from fastapi import APIRouter, Response

from backend.api.v1.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshRequest,
    RefreshResponse,
)
from backend.api.v1.utils import to_user_out
from backend.app_config.settings import settings
from backend.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    user, access, refresh = auth_service.login(payload.username, payload.password)
    return LoginResponse(
        tokens={
            "accessToken": access,
            "refreshToken": refresh,
            "expiresIn": settings.JWT_ACCESS_EXPIRE_SECONDS,
            "tokenType": "Bearer",
        },
        user=to_user_out(user.to_dict()),
    )


@router.post("/refresh", response_model=RefreshResponse)
def refresh(payload: RefreshRequest):
    access, new_refresh = auth_service.refresh_tokens(payload.refreshToken)
    return RefreshResponse(
        tokens={
            "accessToken": access,
            "refreshToken": new_refresh or payload.refreshToken,
            "expiresIn": settings.JWT_ACCESS_EXPIRE_SECONDS,
            "tokenType": "Bearer",
        }
    )


@router.post("/logout", status_code=204)
def logout(payload: LogoutRequest | None = None):
    token = payload.refreshToken if payload else None
    auth_service.logout(token)
    return Response(status_code=204)
