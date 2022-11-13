import os

from bcrypt import checkpw, hashpw

from ...utils.exceptions import ObjectNotFoundException
from . import User

# Generated using bcrypt.gensalt()
SECURITY_PASSWORD_SALT = os.environ.get(
    "SECURITY_PASSWORD_SALT", "$2b$12$.XUdPlluUL7CCg5tOUBm9u"
)


def verify(user: User, password: str) -> bool:
    return checkpw(password.encode("utf-8"), user["password"].encode("utf-8"))


def update_password(user: User, old_password: str, new_password: str) -> bool:
    if not verify(user, old_password):
        return False

    user["password"] = hash_password(new_password)
    user.save()

    return True


def hash_password(password: str) -> str:
    return hashpw(
        password.encode("utf-8"), SECURITY_PASSWORD_SALT.encode("utf-8")
    ).decode("utf-8")


def create_user(email: str, password: str, role="standard") -> bool:
    user = User.objects(email=email).first()

    if user is not None:
        return False

    User(email=email, password=hash_password(password), role=role).save()

    return True


def get_user(email: str) -> User | None:
    return User.objects(email=email).first()


def update_user(user_id: str, payload: dict) -> bool:
    user = User.objects(id=user_id).first()

    if user is None:
        raise ObjectNotFoundException(User)

    if payload["oldPassword"] != payload["newPassword"] and not update_password(
        user, payload["oldPassword"], payload["newPassword"]
    ):
        return False

    user["role"] = payload["role"]
    user.save()

    return True


def delete_user(user_id: str):
    user = User.objects(id=user_id).first()

    if user is None:
        raise ObjectNotFoundException(User)

    user.delete()
