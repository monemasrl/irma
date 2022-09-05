from ..services.database import Organization
from .exceptions import ObjectNotFoundException


def get_organizations():
    organizations = Organization.objects()

    if len(organizations) == 0:
        raise ObjectNotFoundException(Organization)

    return organizations


def create_organization(name: str) -> Organization:
    organization = Organization.objects(organizationName=name).first()

    if organization is not None:
        raise ObjectNotFoundException(Organization)

    organization = Organization(organizationName=name)
    organization.save()

    return organization
