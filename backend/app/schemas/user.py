from uuid import UUID

from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str


class UserResponse(BaseModel, from_attributes=True):
    id: UUID
    name: str


class ListUsers(BaseModel):
    users: list[UserResponse]
    count: int
