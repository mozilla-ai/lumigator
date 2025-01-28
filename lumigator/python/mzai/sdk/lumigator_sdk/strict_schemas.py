from typing import Literal

from lumigator_schemas.completions import CompletionResponse
from lumigator_schemas.datasets import DatasetDownloadResponse, DatasetResponse
from lumigator_schemas.experiments import (
    ExperimentCreate,
    ExperimentResponse,
    ExperimentResultDownloadResponse,
    ExperimentResultResponse,
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
from pydantic import ConfigDict


class CompletionResponse(CompletionResponse):
    model_config = ConfigDict(extra="forbid")


class DatasetDownloadResponse(DatasetDownloadResponse):
    model_config = ConfigDict(extra="forbid")


class DatasetResponse(DatasetResponse, from_attributes=True):
    model_config = ConfigDict(extra="forbid")


class ExperimentCreate(ExperimentCreate):
    model_config = ConfigDict(extra="forbid")


class ExperimentResponse(ExperimentResponse, from_attributes=True):
    model_config = ConfigDict(extra="forbid")


class ExperimentResultResponse(ExperimentResultResponse, from_attributes=True):
    model_config = ConfigDict(extra="forbid")


class ExperimentResultDownloadResponse(ExperimentResultDownloadResponse):
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
