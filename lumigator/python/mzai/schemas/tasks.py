import datetime
from uuid import UUID

from pydantic import BaseModel


class TaskCreate(BaseModel):
    name: str
    description: str = ""
    models: list[str]


class TaskResponse(BaseModel, from_attributes=True):
    id: UUID
    name: str
    description: str
    created_at: datetime.datetime
    models: list[str]
