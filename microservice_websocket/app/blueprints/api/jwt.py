# @jwt_bp.route("/refresh", methods=["POST"])
# @jwt_required(refresh=True)
# def refresh_token():
#     identity = get_jwt_identity()
#     print(type(identity))
#     if identity is None:
#         return {"message": "User Not Found"}, 401
#
#     access_token = create_access_token(identity=identity)
#     return jsonify(access_token=access_token)

from fastapi import APIRouter
from pydantic import BaseModel

from ...services.database.user_manager import auth_user
from ...services.jwt import create_access_token, credentials_exception

jwt_router = APIRouter(prefix="/jwt")


class AuthPayload(BaseModel):
    email: str
    password: str


@jwt_router.post("/authenticate")
async def authenticate_route(payload: AuthPayload):
    if not await auth_user(payload.email, payload.password):
        raise credentials_exception

    access_token: str = create_access_token(payload.email)

    return {"access_token": access_token}
