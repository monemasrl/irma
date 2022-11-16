from fastapi import APIRouter, Depends, Header

from ...services.database import User
from ...services.jwt import get_user_from_jwt
from ...utils.api_token import verify_api_token

test_router = APIRouter(prefix="/test")


@test_router.get("/api-token-test")
def api_token_test(authorization: str | None = Header(default=None)):
    verify_api_token(authorization)
    return {"message": "Valid API Token!"}


@test_router.get("/jwt-test")
async def test_rotue(user: User = Depends(get_user_from_jwt)):
    return {"message": f"Hi {user.email}"}
