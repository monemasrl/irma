from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...services.database import Organization
from ...services.jwt import jwt_required
from ...utils.organization import create_organization, get_organizations

organization_router = APIRouter(prefix="/organizations")


class GetOrgsResponse(BaseModel):
    organizations: list[Organization]


class CreateOrgPayload(BaseModel):
    name: str


@organization_router.get(
    "/", dependencies=[Depends(jwt_required)], response_model=GetOrgsResponse
)
async def get_organizations_route():
    organizations = await get_organizations()

    return {"organizations": organizations}


@organization_router.post(
    "/create", dependencies=[Depends(jwt_required)], response_model=Organization
)
async def create_organization_route(payload: CreateOrgPayload):
    organization = await create_organization(payload.name)

    return organization
