from fastapi import APIRouter, Depends

from ..services.database import User
from ..services.jwt import get_user_from_jwt

test_router = APIRouter(prefix="/test")


@test_router.get("/jwt-test", tags=["test"])
async def test_route(user: User = Depends(get_user_from_jwt)):
    return {"message": f"Hi {user.email}"}
