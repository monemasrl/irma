from beanie import PydanticObjectId

from ..services.database import Application, Organization
from .exceptions import DuplicateException, NotFoundException


async def get_applications(organizationID: str) -> list[Application]:
    organization = await Organization.get(PydanticObjectId(organizationID))
    if organization is None:
        raise NotFoundException("Organization")

    return await Application.find(Application.organization == organization).to_list()


async def create_application(organizationID: str, name: str) -> Application:
    organization = await Organization.get(PydanticObjectId(organizationID))
    if organization is None:
        raise NotFoundException("Organization")

    application = await Application.find_one(
        Application.applicationName == name
        and Application.organization == organization,
    )
    if application is not None:
        raise DuplicateException("applicationName")

    application = Application(
        applicationName=name, organization=Organization.link_from_id(organization.id)
    )
    await application.save()

    return application
