from ..services.database import Application, Organization
from .exceptions import ObjectAttributeAlreadyUsedException, ObjectNotFoundException


def get_applications(organizationID: str):
    applications = Application.objects(organization=organizationID)

    if len(applications) == 0:
        raise ObjectNotFoundException(Application)

    return applications


def create_application(organizationID: str, name: str) -> Application:
    application = Application.objects(applicationName=name).first()

    if application is not None:
        raise ObjectAttributeAlreadyUsedException(application["applicationName"])

    organization = Organization.objects(id=organizationID).first()

    if organization is None:
        raise ObjectNotFoundException(Organization)

    application = Application(applicationName=name, organization=organization)
    application.save()
    return application
