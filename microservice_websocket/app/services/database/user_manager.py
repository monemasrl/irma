# import os
#
# from bcrypt import checkpw, hashpw
#
# from . import User
#
# # Generated using bcrypt.gensalt()
# SECURITY_PASSWORD_SALT = os.environ.get(
#     "SECURITY_PASSWORD_SALT", "$2b$12$.XUdPlluUL7CCg5tOUBm9u"
# )
#
#
# def verify(user: User, password: str) -> bool:
#     return checkpw(password.encode("utf-8"), user["password"].encode("utf-8"))
#
#
# def hash_password(password: str) -> str:
#     return hashpw(
#         password.encode("utf-8"), SECURITY_PASSWORD_SALT.encode("utf-8")
#     ).decode("utf-8")
#
#
# def create_user(email: str, password: str, role="standard") -> bool:
#     user = User.objects(email=email).first()
#
#     if user is not None:
#         return False
#
#     User(email=email, password=hash_password(password), role=role).save()
#
#     return True
#
#
# def get_user(email: str) -> User | None:
#     return User.objects(email=email).first()

from typing import Optional

from passlib.context import CryptContext

from ..database import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


async def auth_user(email: str, password: str) -> Optional[User]:
    user = await User.find(User.email == email).first_or_none()

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_user_from_mail(email: str) -> Optional[User]:
    return await User.find(User.email == email).first_or_none()


async def create_user(email: str, password: str) -> Optional[User]:
    if await get_user_from_mail(email):
        return None

    user = User(email=email, hashed_password=hash_password(password))
    await user.save()
    return user
