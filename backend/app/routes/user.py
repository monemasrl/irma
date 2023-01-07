from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..controllers.user import (
    create_user,
    delete_user,
    get_user_info,
    get_user_list,
    update_user,
)
from ..services.database import User
from ..services.jwt import get_user_from_jwt
from ..utils.admin import verify_admin
from .models import CreateUserPayload, UpdateUserPayload

user_router = APIRouter()


class UserListResponse(BaseModel):
    users: list[User.Serialized]


@user_router.get("/users", response_model=UserListResponse, tags=["user"])
async def get_user_list_route(user: User = Depends(get_user_from_jwt)):
    verify_admin(user)

    users: list[User] = await get_user_list()

    return {"users": [x.serialize() for x in users]}


@user_router.get("/user/{user_id}", response_model=User.Serialized, tags=["user"])
async def get_user_info_route(user_id: str, user: User = Depends(get_user_from_jwt)):
    verify_admin(user)

    user_info = await get_user_info(user_id)

    return user_info.serialize()


@user_router.get("/user", response_model=User.Serialized, tags=["user"])
async def get_own_user_info_route(user: User = Depends(get_user_from_jwt)):
    return user.serialize()


@user_router.post("/user", tags=["user"])
async def create_user_route(
    payload: CreateUserPayload, user: User = Depends(get_user_from_jwt)
):
    verify_admin(user)

    if not await create_user(payload):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User Already Existing"
        )

    return {"message": "Created"}


@user_router.put("/user/{user_id}", tags=["user"])
async def update_user_route(
    payload: UpdateUserPayload, user_id: str, user: User = Depends(get_user_from_jwt)
):
    if str(user.id) != user_id:
        verify_admin(user)

    if not await update_user(user_id, payload):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Old Password Doesn't Match",
        )

    return {"message": "Updated"}


@user_router.delete("/user/{user_id}", tags=["user"])
async def delete_user_route(user_id: str, user: User = Depends(get_user_from_jwt)):
    if str(user.id) == user_id:
        return {"message": "Cannot Delete Current Active User"}, 400

    verify_admin(user)

    await delete_user(user_id)

    return {"message": "Deleted"}
