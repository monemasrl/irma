from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..controllers.application import create_application, get_applications
from ..services.database import Application
from ..services.jwt import jwt_required

application_router = APIRouter()


class GetOrgsResponse(BaseModel):
    applications: list[Application.Serialized]


class CreateAppPayload(BaseModel):
    name: str
    organizationID: str


@application_router.get(
    "/applications",
    dependencies=[Depends(jwt_required)],
    response_model=GetOrgsResponse,
    tags=["application"],
)
async def get_applications_route(organizationID: str):
    applications = await get_applications(organizationID)

    return {"applications": [x.serialize() for x in applications]}


@application_router.post("/application", tags=["application"])
async def create_application_route(payload: CreateAppPayload):
    await create_application(payload.organizationID, payload.name)

    return {"message": "Created"}
