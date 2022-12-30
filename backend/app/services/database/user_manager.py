from typing import Optional

from beanie import PydanticObjectId
from passlib.context import CryptContext

from ...exceptions import NotFoundException
from ...routes.models import UpdateUserPayload
from ..database import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def update_password(user: User, old_password: str, new_password: str) -> bool:
    if not await auth_user(user.email, old_password):
        return False

    user.hashed_password = hash_password(new_password)
    await user.save()

    return True


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


async def create_user(
    email: str, password: str, first_name: str, last_name: str, role: str = "standard"
) -> Optional[User]:
    if await get_user_from_mail(email):
        return None

    user = User(
        email=email,
        hashed_password=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        role=role,
    )
    await user.save()
    return user


async def update_user(user_id: str, payload: UpdateUserPayload) -> bool:
    user = await User.get(PydanticObjectId(user_id))
    if user is None:
        raise NotFoundException("User")

    if payload.email is not None:
        user.email = payload.email

    if payload.first_name is not None:
        user.first_name = payload.first_name

    if payload.last_name is not None:
        user.last_name = payload.last_name

    if payload.role is not None:
        user.role = payload.role

    if (
        payload.old_password
        and payload.new_password
        and payload.old_password != payload.new_password
        and not await update_password(user, payload.old_password, payload.new_password)
    ):
        return False

    await user.save()

    return True


async def delete_user(user_id: str):
    user = await User.get(PydanticObjectId(user_id))
    if user is None:
        raise NotFoundException("User")

    await user.delete()
