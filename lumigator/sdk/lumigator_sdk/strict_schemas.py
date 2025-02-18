from lumigator_schemas.datasets import DatasetDownloadResponse, DatasetResponse
from lumigator_schemas.experiments import (
    ExperimentCreate,
    GetExperimentResponse,
)
from lumigator_schemas.extras import HealthResponse, ListingResponse
from lumigator_schemas.jobs import (
    Job,
    JobAnnotateConfig,
    JobCreate,
    JobEvalConfig,
    JobEvent,
    JobInferenceConfig,
    JobLogsResponse,
    JobResponse,
    JobResultDownloadResponse,
    JobResultResponse,
    JobSubmissionResponse,
)
from lumigator_schemas.workflows import WorkflowCreateRequest
from pydantic import ConfigDict


class DatasetDownloadResponse(DatasetDownloadResponse):
    model_config = ConfigDict(extra="forbid")


class DatasetResponse(DatasetResponse, from_attributes=True):
    model_config = ConfigDict(extra="forbid")


class ExperimentCreate(ExperimentCreate):
    model_config = ConfigDict(extra="forbid")


class GetExperimentResponse(GetExperimentResponse, from_attributes=True):
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
    model_config = ConfigDict(extra="forbid")


class JobEvalConfig(JobEvalConfig):
    model_config = ConfigDict(extra="forbid")


class JobAnnotateConfig(JobAnnotateConfig):
    model_config = ConfigDict(extra="forbid")


class JobResponse(JobResponse, from_attributes=True):
    model_config = ConfigDict(extra="forbid")


class JobResultResponse(JobResultResponse, from_attributes=True):
    model_config = ConfigDict(extra="forbid")


class JobResultDownloadResponse(JobResultDownloadResponse):
    model_config = ConfigDict(extra="forbid")


class WorkflowCreateRequest(WorkflowCreateRequest):
    model_config = ConfigDict(extra="forbid")
