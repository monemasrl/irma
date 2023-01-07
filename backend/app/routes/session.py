from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..controllers.session import get_session, get_sessions_id
from ..services.database import Reading
from ..services.jwt import jwt_required

session_router = APIRouter()


class GetSessionResponse(BaseModel):
    readings: list[Reading.Aggregated]


class GetSessionIDsResponse(BaseModel):
    IDs: list[int]


@session_router.get(
    "/session/{sessionID}",
    dependencies=[Depends(jwt_required)],
    response_model=GetSessionResponse,
    tags=["session"],
)
async def get_reading_session(nodeID: int, sessionID: int):
    readings = await get_session(nodeID, sessionID)

    return {"readings": readings}


@session_router.get(
    "/session",
    dependencies=[Depends(jwt_required)],
    response_model=GetSessionResponse,
    tags=["session"],
)
async def get_reading_session_no_sessionID(nodeID: int):
    readings = await get_session(nodeID, None)

    return {"readings": readings}


@session_router.get(
    "/sessions",
    dependencies=[Depends(jwt_required)],
    response_model=GetSessionIDsResponse,
    tags=["session"],
)
async def get_sessions_id_route(nodeID: int):
    sessions_id = await get_sessions_id(nodeID)

    return {"IDs": sessions_id}
