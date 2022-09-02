import os

from bcrypt import checkpw, hashpw

from . import User

# Generated using bcrypt.gensalt()
SECURITY_PASSWORD_SALT = os.environ.get(
    "SECURITY_PASSWORD_SALT", "$2b$12$.XUdPlluUL7CCg5tOUBm9u"
)


def verify(user: User, password: str) -> bool:
    return checkpw(password.encode("utf-8"), user["password"].encode("utf-8"))


def hash_password(password: str) -> str:
    return hashpw(
        password.encode("utf-8"), SECURITY_PASSWORD_SALT.encode("utf-8")
    ).decode("utf-8")


def create_user(email: str, password: str) -> bool:
    user = User.objects(email=email).first()

    if user is not None:
        return False

    User(email=email, password=hash_password(password)).save()

    return True


def get_user(email: str) -> User | None:
    return User.objects(email=email).first()
