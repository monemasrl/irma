from ..services.database import Organization
from .exceptions import DuplicateException


async def get_organizations() -> list[Organization]:
    return await Organization.find_all().to_list()


async def create_organization(name: str) -> Organization:
    organization = await Organization.find_one(Organization.organizationName == name)

    if organization is not None:
        raise DuplicateException("organizationName")

    organization = Organization(organizationName=name)
    await organization.save()

    return organization
