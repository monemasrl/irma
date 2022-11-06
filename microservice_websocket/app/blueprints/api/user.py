from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...services.database.models import User
from ...services.jwt import get_user_from_jwt

user_router = APIRouter(prefix="/user")


class UserInfoResponse(BaseModel):
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str


@user_router.get("/info", response_model=UserInfoResponse)
def get_user_info_route(user: User = Depends(get_user_from_jwt)):

    return UserInfoResponse(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
    )
