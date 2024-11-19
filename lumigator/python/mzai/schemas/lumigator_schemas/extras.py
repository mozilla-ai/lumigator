from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

ItemType = TypeVar("ItemType")


class DeploymentType(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    status: str
    deployment_type: DeploymentType


class ListingResponse(BaseModel, Generic[ItemType]):
    model_config = ConfigDict(extra='forbid')
    total: int
    items: list[ItemType]
