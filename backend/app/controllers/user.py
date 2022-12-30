from beanie import PydanticObjectId

from ..exceptions import NotFoundException
from ..routes.models import CreateUserPayload, UpdateUserPayload
from ..services.database import User, user_manager


async def get_user_list() -> list[User]:
    return await User.find_all().to_list()


async def get_user_info(user_id: str) -> User:
    user = await User.get(PydanticObjectId(user_id))

    if user is None:
        raise NotFoundException("User")

    return user


async def create_user(payload: CreateUserPayload) -> User | None:
    return await user_manager.create_user(
        email=payload.email,
        password=payload.password,
        role=payload.role,
        first_name=payload.first_name,
        last_name=payload.last_name,
    )


async def update_user(user_id: str, payload: UpdateUserPayload) -> bool:
    return await user_manager.update_user(user_id, payload)


async def delete_user(user_id: str):
    await user_manager.delete_user(user_id)
