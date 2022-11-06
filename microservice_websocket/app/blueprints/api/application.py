from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...services.database import Application
from ...services.jwt import jwt_required
from ...utils.application import create_application, get_applications

application_router = APIRouter(prefix="/applications")


class GetOrgsResponse(BaseModel):
    applications: list[Application]


class CreateAppPayload(BaseModel):
    name: str
    organizationID: str


@application_router.get(
    "/", dependencies=[Depends(jwt_required)], response_model=GetOrgsResponse
)
async def get_applications_route(organizationID: str):
    applications = await get_applications(organizationID)

    return {"applications": applications}


@application_router.post("/create")
async def create_application_route(payload: CreateAppPayload):
    application = await create_application(payload.organizationID, payload.name)

    return application
