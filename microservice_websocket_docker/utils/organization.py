from services.database import Organization


def get_organizations():
    return Organization.objects()


def create_organization(name: str) -> Organization:
    organization = Organization(organizationName=name)
    organization.save()

    return organization
