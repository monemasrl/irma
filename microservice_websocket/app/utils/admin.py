from fastapi import HTTPException, status

from ..services.database.models import User


def verify_admin(user: User):
    not_an_admin_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin Privileges Required"
    )

    if user.role != "admin":
        raise not_an_admin_exception
