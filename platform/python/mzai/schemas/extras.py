from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel

ItemType = TypeVar("ItemType")


class DeploymentType(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class HealthResponse(BaseModel):
    status: str
    deployment_type: DeploymentType


class ListingResponse(BaseModel, Generic[ItemType]):
    total: int
    items: list[ItemType]
