from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...services.database import Node
from ...services.jwt import jwt_required
from ...utils.node import get_nodes

node_router = APIRouter(prefix="/nodes")


class GetNodesResponse(BaseModel):
    nodes: list[Node]


@node_router.get(
    "/", dependencies=[Depends(jwt_required)], response_model=GetNodesResponse
)
async def get_nodes_route(applicationID: str):
    nodes: list[Node] = await get_nodes(applicationID)

    return {"nodes": nodes}
