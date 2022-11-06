# from flask_jwt_extended import JWTManager
# from ..database import user_manager
#
#
# def init_jwt(app):
#     jwt = JWTManager(app)
#
#     # Register a callback function that loads a user from your database whenever
#     # a protected route is accessed. This should return any python object on a
#     # successful lookup, or None if the lookup failed for any reason (for example
#     # if the user has been deleted from the database).
#     @jwt.user_lookup_loader
#     def user_lookup_callback(_jwt_header, jwt_data):
#         identity = jwt_data["sub"]
#         app.logger.info(f"{identity=}")
#         return user_manager.get_user(identity["email"])

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from ..database import User
from ..database.user_manager import get_user_from_mail

# TODO: move to config
SECRET_KEY = "2f74b51642e77be0adf1c1d61ca95fd47a2a458f2859362f93e2af53cd002ecd"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_access_token(email: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode = {"sub": email, "exp": expire}

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_user_from_jwt(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_from_mail(email)
    if user is None:
        raise credentials_exception

    return user


async def jwt_required(token: str = Depends(oauth2_scheme)):
    await get_user_from_jwt(token)
