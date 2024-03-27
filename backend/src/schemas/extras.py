from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from src.settings import DeploymentType

ItemType = TypeVar("ItemType")


class JobStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"
    SUCCEEDED = "succeeded"


class HealthResponse(BaseModel):
    status: str = Field(..., example="OK")
    deployment_type: DeploymentType = Field(..., example=DeploymentType.PRODUCTION)


class ListingResponse(BaseModel, Generic[ItemType]):
    total: int
    items: list[ItemType]
