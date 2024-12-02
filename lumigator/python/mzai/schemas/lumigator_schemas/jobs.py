import datetime as dt
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class JobType(str, Enum):
    INFERENCE = "inference"
    EVALUATION = "evaluate"


class JobStatus(str, Enum):
    CREATED = "created"
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    SUCCEEDED = "succeeded"


class JobConfig(BaseModel):
    job_id: UUID
    job_type: JobType
    command: str
    args: dict[str, Any] | None = None


class JobEvent(BaseModel):
    job_id: UUID
    job_type: JobType
    status: JobStatus
    detail: str | None = None


class JobLogsResponse(BaseModel):
    logs: str | None = None


class JobSubmissionResponse(BaseModel):
    type: str | None = None
    job_id: str | None = None
    submission_id: str | None = None
    driver_info: str | None = None
    status: str | None = None
    entrypoint: str | None = None
    message: str | None = None
    error_type: str | None = None
    start_time: dt.datetime | None = None
    end_time: dt.datetime | None = None
    metadata: dict = Field(default_factory=dict)
    runtime_env: dict = Field(default_factory=dict)
    driver_agent_http_address: str | None = None
    driver_node_id: str | None = None
    driver_exit_code: int | None = None


class JobEvalCreate(BaseModel):
    name: str
    description: str = ""
    model: str
    dataset: UUID
    max_samples: int = -1  # set to all samples by default
    model_url: str | None = None
    system_prompt: str | None = None
    config_template: str | None = None


class JobInferenceCreate(BaseModel):
    name: str
    description: str = ""
    model: str
    dataset: UUID
    max_samples: int = -1  # set to all samples by default
    model_url: str | None = None
    system_prompt: str | None = None
    output_field: str | None = "prediction"
    max_tokens: int = 1024
    frequency_penalty: float = 0.0
    temperature: float = 1.0
    top_p: float = 1.0
    config_template: str | None = None


class JobResponse(BaseModel, from_attributes=True):
    id: UUID
    name: str
    description: str
    status: JobStatus
    created_at: dt.datetime
    updated_at: dt.datetime | None = None


class JobResultResponse(BaseModel, from_attributes=True):
    id: UUID
    job_id: UUID


class JobResultDownloadResponse(BaseModel):
    id: UUID
    download_url: str
