from enum import Enum

from pydantic import BaseModel, Field

from src.settings import DeploymentType


class JobStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    FAILED = "failed"


class Health(BaseModel):
    status: str = Field(..., example="Ok")
    deployment_type: DeploymentType = Field(..., example=DeploymentType.PRODUCTION)
