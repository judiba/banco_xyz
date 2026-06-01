from __future__ import annotations

from fastapi import APIRouter

from backend.api.v1.deps import CurrentUser
from backend.api.v1.schemas.user import UserOut
from backend.api.v1.utils import to_user_out

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(user: CurrentUser):
    return to_user_out(user.to_dict())
