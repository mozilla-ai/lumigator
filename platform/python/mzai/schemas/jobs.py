from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class JobType(str, Enum):
    EXPERIMENT = "experiment"
    FINETUNING = "finetuning"


class JobStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    FAILED = "failed"
    SUCCEEDED = "succeeded"


class JobConfig(BaseModel):
    id: UUID
    type: JobType
    args: dict[str, Any]
