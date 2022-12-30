from fastapi import APIRouter
from pydantic import BaseModel

from ..services.jwt import create_access_token, credentials_exception

jwt_router = APIRouter(prefix="/jwt")


class AuthPayload(BaseModel):
    email: str
    password: str


@jwt_router.post("/")
async def authenticate_route(payload: AuthPayload):
    from ..services.database.user_manager import auth_user

    if not await auth_user(payload.email, payload.password):
        raise credentials_exception

    access_token: str = create_access_token(payload.email)

    return {"access_token": access_token}
