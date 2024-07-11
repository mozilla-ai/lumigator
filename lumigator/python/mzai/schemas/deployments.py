from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class DeploymentType(str, Enum):
    GROUNDTRUTH = "groundtruth"


# todo: check Ray Status for serve
class DeploymentStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    FAILED = "failed"
    SUCCEEDED = "succeeded"


class DeploymentConfig(BaseModel):
    deployment_id: UUID | None = None
    deployment_type: DeploymentType | None = None
    args: dict[str, Any] | None = None


class DeploymentEvent(BaseModel):
    deployment_id: UUID
    deployment_type: DeploymentType
    status: DeploymentStatus
    detail: str | None = None
