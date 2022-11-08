from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...services.jwt import jwt_required
from ...utils.external_archiviation import (
    add_external_endpoint,
    delete_external_endpoint,
    get_external_endpoints,
)

ext_arch_router = APIRouter(prefix="/external-archiviations")


class GetExternalResponse(BaseModel):
    endpoints: list[str]


class ExternalPayload(BaseModel):
    endpoint: str


@ext_arch_router.get(
    "/", dependencies=[Depends(jwt_required)], response_model=GetExternalResponse
)
def get_external_endpoint_route():
    endpoints = get_external_endpoints()

    return {"endpoints": endpoints}


@ext_arch_router.post("/add", dependencies=[Depends(jwt_required)])
def add_external_endpoint_route(payload: ExternalPayload):
    add_external_endpoint(payload.endpoint)

    return {"message": "Inserted"}, 200


@ext_arch_router.delete("/", dependencies=[Depends(jwt_required)])
def delete_external_endpoint_route(endpoint: str):
    delete_external_endpoint(endpoint)

    return {"message": "Deleted"}, 200
