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
    JobAnnotateCreate,
    JobConfig,
    JobEvalCreate,
    JobEvent,
    JobInferenceCreate,
    JobLogsResponse,
    JobResponse,
    JobResultDownloadResponse,
    JobResultResponse,
    JobSubmissionResponse,
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


class JobConfig(JobConfig):
    model_config = ConfigDict(extra="forbid")


class JobEvent(JobEvent):
    model_config = ConfigDict(extra="forbid")


class JobLogsResponse(JobLogsResponse):
    model_config = ConfigDict(extra="forbid")


class JobSubmissionResponse(JobSubmissionResponse):
    model_config = ConfigDict(extra="forbid")


class JobEvalCreate(JobEvalCreate):
    model_config = ConfigDict(extra="forbid")


class JobInferenceCreate(JobInferenceCreate):
    model_config = ConfigDict(extra="forbid")


class JobAnnotateCreate(JobAnnotateCreate):
    model_config = ConfigDict(extra="forbid")


class JobResponse(JobResponse, from_attributes=True):
    model_config = ConfigDict(extra="forbid")


class JobResultResponse(JobResultResponse, from_attributes=True):
    model_config = ConfigDict(extra="forbid")


class JobResultDownloadResponse(JobResultDownloadResponse):
    model_config = ConfigDict(extra="forbid")
