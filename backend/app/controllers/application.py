from beanie import PydanticObjectId
from beanie.operators import And, Eq

from ..exceptions import DuplicateException, NotFoundException
from ..services.database import Application, Organization


async def get_applications(organizationID: str) -> list[Application]:
    organization = await Organization.get(PydanticObjectId(organizationID))
    if organization is None:
        raise NotFoundException("Organization")

    return await Application.find(Application.organization == organization.id).to_list()


async def create_application(organizationID: str, name: str) -> Application:
    organization = await Organization.get(PydanticObjectId(organizationID))
    if organization is None:
        raise NotFoundException("Organization")

    application = await Application.find_one(
        And(
            Eq(Application.applicationName, name),
            Eq(Application.organization, organization.id),
        )
    )
    if application is not None:
        raise DuplicateException("applicationName")

    application = Application(
        applicationName=name, organization=PydanticObjectId(organizationID)
    )
    await application.save()

    return application
