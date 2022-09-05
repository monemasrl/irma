from ..services.database import Application, Organization


def get_applications(organizationID: str):
    applications = Application.objects(organization=organizationID)

    return applications


def create_application(organizationID: str, name: str) -> Application:
    organization = Organization.objects(id=organizationID).first()

    application = Application(applicationName=name, organization=organization)
    application.save()
    return application
