from typing import Union

from ..services.database import Application, Organization


def get_applications(organizationID: str) -> tuple[dict, int]:
    return Application.objects(organization=organizationID)


def create_application(organizationID: str, name: str) -> Union[Application, None]:
    organizations = Organization.objects(id=organizationID)

    if len(organizations) > 0:
        organization = organizations[0]
        application = Application(applicationName=name, organization=organization)
        application.save()
        return application

    return None
