import datetime as dt
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LowercaseEnum(str, Enum):
    """Can be used to ensure that values for enums are returned in lowercase."""

    def __new__(cls, value):
        obj = super().__new__(cls, value.lower())
        obj._value_ = value.lower()
        return obj


class JobType(LowercaseEnum):
    INFERENCE = "inference"
    EVALUATION = "evaluate"
    EVALUATION_LITE = "eval_lite"
    ANNOTATION = "annotate"


class JobStatus(LowercaseEnum):
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
    skip_inference: bool = False


# TODO: this has to be renamed to JobEvalCreate and the code above
#       has to be removed when we deprecate evaluator
class JobEvalLiteCreate(BaseModel):
    name: str
    description: str = ""
    model: str
    dataset: UUID
    max_samples: int = -1  # set to all samples by default
    config_template: str | None = None


class JobInferenceCreate(BaseModel):
    name: str
    description: str = ""
    model: str
    dataset: UUID
    max_samples: int = -1  # set to all samples by default
    task: str | None = "summarization"
    accelerator: str | None = "auto"
    revision: str | None = "main"
    use_fast: bool = True  # Whether or not to use a Fast tokenizer if possible
    trust_remote_code: bool = False
    torch_dtype: str = "auto"
    model_url: str | None = None
    system_prompt: str | None = None
    output_field: str | None = "predictions"
    max_tokens: int = 1024
    frequency_penalty: float = 0.0
    temperature: float = 1.0
    top_p: float = 1.0
    config_template: str | None = None
    store_to_dataset: bool = False


class JobAnnotateCreate(BaseModel):
    name: str
    description: str = ""
    dataset: UUID
    max_samples: int = -1  # set to all samples by default
    task: str | None = "summarization"
    store_to_dataset: bool = False


class JobResponse(BaseModel, from_attributes=True):
    id: UUID
    name: str
    description: str
    status: JobStatus
    created_at: dt.datetime
    experiment_id: UUID | None = None
    updated_at: dt.datetime | None = None


class JobResultResponse(BaseModel, from_attributes=True):
    id: UUID
    job_id: UUID


class JobResultDownloadResponse(BaseModel):
    id: UUID
    download_url: str


class JobResults(BaseModel):
    id: UUID
    metrics: list[dict[str, Any]] | None = None
    parameters: list[dict[str, Any]] | None = None
    metric_url: str
    artifact_url: str


class JobResultObject(BaseModel):
    """This is a very loose definition of what data
    should be stored in the output settings.S3_JOB_RESULTS_FILENAME.
    As long as a job result file only has the fields defined here,
    it should be accepted by the backend.
    """

    model_config = ConfigDict(extra="forbid")
    metrics: dict | None
    parameters: dict | None
    artifacts: dict | None


class Job(JobResponse, JobSubmissionResponse):
    """Job represents the composition of JobResponse and JobSubmissionResponse.

    JobSubmissionResponse was formerly returned from some /health/jobs related
    endpoints, while JobResponse was used by /jobs related endpoints.

    The only conflicting field in the two schemas is 'status' which is consistent
    in what it intends to represent, but uses different types (JobStatus/str).

    The Job type has both id and submission_id which will contain the same data.

    NOTE: Job is intended to reduce breaking changes experienced by the UI and other
    consumers. Tt was not conceived as a type that will be around for long, as
    the API needs to be refactored to better support experiments.
    """

    pass
