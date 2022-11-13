from typing import Optional

from ..services.database import User, user_manager


def get_user_list():
    return list(User.objects())


def get_user_info(user_id: str) -> Optional[User]:
    return User.objects(id=user_id).first()


def create_user(payload: dict) -> bool:
    return user_manager.create_user(
        email=payload["email"], password=payload["password"], role=payload["role"]
    )


def update_user(user_id: str, payload: dict) -> bool:
    return user_manager.update_user(user_id, payload)


def delete_user(user_id: str):
    user_manager.delete_user(user_id)
