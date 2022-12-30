from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..controllers.organization import create_organization, get_organizations
from ..services.database import Organization
from ..services.jwt import jwt_required

organization_router = APIRouter()


class GetOrgsResponse(BaseModel):
    organizations: list[Organization.Serialized]


class CreateOrgPayload(BaseModel):
    name: str


@organization_router.get(
    "/organizations",
    dependencies=[Depends(jwt_required)],
    response_model=GetOrgsResponse,
)
async def get_organizations_route():
    organizations = await get_organizations()

    return {"organizations": [x.serialize() for x in organizations]}


@organization_router.post("/organization", dependencies=[Depends(jwt_required)])
async def create_organization_route(payload: CreateOrgPayload):
    await create_organization(payload.name)

    return {"message": "Created"}
