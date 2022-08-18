import os

from bcrypt import hashpw, checkpw
import database as db

# Generated using bcrypt.gensalt()
SECURITY_PASSWORD_SALT = os.environ.get(
    "SECURITY_PASSWORD_SALT", '$2b$12$.XUdPlluUL7CCg5tOUBm9u')


def verify(user: db.User, password: str) -> bool:
    return checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))


def hash_password(password: str) -> str:
    return hashpw(
        password.encode('utf-8'),
        SECURITY_PASSWORD_SALT.encode('utf-8')
    ).decode('utf-8')


def create_user(email: str, password: str) -> bool:
    user = db.User.objects(email=email).first()

    if user is not None:
        return False

    db.User(
        email=email,
        password=hash_password(password)
    ).save()

    return True


def get_user(email: str) -> db.User | None:
    return db.User.objects(email=email).first()
