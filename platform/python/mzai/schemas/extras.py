from typing import Generic, TypeVar

from pydantic import BaseModel

from mzai.backend.settings import DeploymentType

ItemType = TypeVar("ItemType")


class HealthResponse(BaseModel):
    status: str
    deployment_type: DeploymentType


class ListingResponse(BaseModel, Generic[ItemType]):
    total: int
    items: list[ItemType]
