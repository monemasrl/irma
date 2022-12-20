from pydantic import BaseModel


class HandlePayload(BaseModel):
    isConfirmed: bool
    handleNote: str


class CreateUserPayload(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    role: str


class UpdateUserPayload(BaseModel):
    email: str | None = None
    first_name: str | None
    last_name: str | None
    old_password: str | None = None
    new_password: str | None = None
    role: str | None = None
