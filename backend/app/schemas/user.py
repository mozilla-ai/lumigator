from uuid import UUID

from pydantic import BaseModel


class UserSchema(BaseModel, from_attributes=True):
    id: UUID
    name: str


class UserCreate(BaseModel):
    name: str


class ListUsers(BaseModel):
    users: list[UserSchema]
    count: int
