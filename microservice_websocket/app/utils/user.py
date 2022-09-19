from typing import Optional

from ..services.database import User


def get_user_info(user_id: str) -> Optional[User]:
    return User.objects(id=user_id).first()
