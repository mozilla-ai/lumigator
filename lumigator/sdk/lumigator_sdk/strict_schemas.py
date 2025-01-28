from typing import Literal

from lumigator_schemas.datasets import DatasetDownloadResponse, DatasetResponse
from lumigator_schemas.experiments import (
    ExperimentIdCreate,
    ExperimentResponse,
)
from lumigator_schemas.extras import HealthResponse, ListingResponse
from lumigator_schemas.jobs import (
    Job,
    JobAnnotateConfig,
    JobCreate,
    JobEvalLiteConfig,
    JobEvent,
    JobInferenceConfig,
    JobLogsResponse,
    JobResponse,
    JobResultDownloadResponse,
    JobResultResponse,
    JobSubmissionResponse,
    JobType,
)
from lumigator_schemas.workflows import WorkflowCreateRequest
from pydantic import ConfigDict


class DatasetDownloadResponse(DatasetDownloadResponse):
    model_config = ConfigDict(extra="forbid")


class DatasetResponse(DatasetResponse, from_attributes=True):
    model_config = ConfigDict(extra="forbid")


class ExperimentIdCreate(ExperimentIdCreate):
    model_config = ConfigDict(extra="forbid")


class ExperimentResponse(ExperimentResponse, from_attributes=True):
    model_config = ConfigDict(extra="forbid")


class HealthResponse(HealthResponse):
    model_config = ConfigDict(extra="forbid")


class ListingResponse(ListingResponse):
    model_config = ConfigDict(extra="forbid")


class Job(Job):
    model_config = ConfigDict(extra="forbid")


class JobEvent(JobEvent):
    model_config = ConfigDict(extra="forbid")


class JobLogsResponse(JobLogsResponse):
    model_config = ConfigDict(extra="forbid")


class JobSubmissionResponse(JobSubmissionResponse):
    model_config = ConfigDict(extra="forbid")


class JobCreate(JobCreate):
    model_config = ConfigDict(extra="forbid")


class JobInferenceConfig(JobInferenceConfig):
    job_type: Literal[JobType.INFERENCE] = JobType.INFERENCE
    model_config = ConfigDict(extra="forbid")


class JobEvalLiteConfig(JobEvalLiteConfig):
    job_type: Literal[JobType.EVALUATION_LITE] = JobType.EVALUATION_LITE
    model_config = ConfigDict(extra="forbid")


class JobAnnotateConfig(JobAnnotateConfig):
    job_type: Literal[JobType.ANNOTATION] = JobType.ANNOTATION
    model_config = ConfigDict(extra="forbid")


class JobResponse(JobResponse, from_attributes=True):
    model_config = ConfigDict(extra="forbid")


class JobResultResponse(JobResultResponse, from_attributes=True):
    model_config = ConfigDict(extra="forbid")


class JobResultDownloadResponse(JobResultDownloadResponse):
    model_config = ConfigDict(extra="forbid")


class WorkflowCreateRequest(WorkflowCreateRequest):
    model_config = ConfigDict(extra="forbid")
