from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...services.database import Reading
from ...services.jwt import jwt_required
from ...utils.session import get_session, get_sessions_id

session_router = APIRouter(prefix="/session")


class GetSessionResponse(BaseModel):
    readings: list[Reading]


class GetSessionIDsResponse(BaseModel):
    IDs: list[int]


@session_router.get(
    "/", dependencies=[Depends(jwt_required)], response_model=GetSessionResponse
)
async def get_reading_session(nodeID: int, sessionID: int | None = None):
    readings = await get_session(nodeID, sessionID)

    return {"readings": readings}


@session_router.get(
    "/ids", dependencies=[Depends(jwt_required)], response_model=GetSessionIDsResponse
)
async def get_sessions_id_route(nodeID: int):
    sessions_id = await get_sessions_id(nodeID)

    return {"IDs": sessions_id}
