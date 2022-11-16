from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...services.database import User
from ...services.jwt import get_user_from_jwt
from ...utils.admin import verify_admin
from ...utils.user import (
    create_user,
    delete_user,
    get_user_info,
    get_user_list,
    update_user,
)
from .models import CreateUserPayload, UpdateUserPayload

user_router = APIRouter(prefix="/user")


class UserInfoResponse(BaseModel):
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str


@user_router.get("/list", response_model=list[User])
async def get_user_list_route(user: User = Depends(get_user_from_jwt)):
    verify_admin(user)

    users: list[User] = await get_user_list()

    return {"users": users}


@user_router.get("/<user_id>", response_model=UserInfoResponse)
async def get_user_info_route(user_id: str, user: User = Depends(get_user_from_jwt)):
    verify_admin(user)

    user_info = await get_user_info(user_id)

    return UserInfoResponse(
        email=user_info.email,
        first_name=user_info.first_name,
        last_name=user_info.last_name,
        role=user_info.role,
    )


@user_router.post("/create")
def create_user_route(
    payload: CreateUserPayload, user: User = Depends(get_user_from_jwt)
):
    verify_admin(user)

    if not create_user(payload):
        return {"message": "User Already Existing"}, 400

    return {"message": "Created"}, 200


@user_router.put("/<user_id>")
async def update_user_route(
    payload: UpdateUserPayload, user_id: str, user: User = Depends(get_user_from_jwt)
):
    if str(user.id) != user_id:
        verify_admin(user)

    if not await update_user(user_id, payload):
        return {"message": "Old Password Doesn't Match"}, 401

    return {"message": "Updated"}, 200


@user_router.delete("/<user_id>")
async def delete_user_route(user_id: str, user: User = Depends(get_user_from_jwt)):
    if str(user.id) == user_id:
        return {"message": "Cannot Delete Current Active User"}, 400

    verify_admin(user)

    await delete_user(user_id)

    return {"message": "Deleted"}


@user_router.get("/info", response_model=UserInfoResponse)
def get_own_user_info_route(user: User = Depends(get_user_from_jwt)):

    return UserInfoResponse(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
    )
