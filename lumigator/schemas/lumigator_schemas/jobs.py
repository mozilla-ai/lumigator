import datetime as dt
from enum import Enum
from typing import Any, Literal, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from lumigator_schemas.tasks import SummarizationTaskDefinition, TaskDefinition, TaskType

DEFAULT_SUMMARIZATION_PROMPT = "You are a helpful assistant, expert in text summarization. For every prompt you receive, provide a summary of its contents in at most two sentences."  # noqa: E501


class LowercaseEnum(str, Enum):
    """Can be used to ensure that values for enums are returned in lowercase."""

    def __new__(cls, value):
        obj = super().__new__(cls, value.lower())
        obj._value_ = value.lower()
        return obj


class JobType(LowercaseEnum):
    INFERENCE = "inference"
    EVALUATION = "evaluator"
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


# Check Ray items actually used and copy
# those from the schema
# ref to https://docs.ray.io/en/latest/cluster/running-applications/job-submission/doc/ray.job_submission.JobDetails.html
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


class JobEvalConfig(BaseModel):
    job_type: Literal[JobType.EVALUATION] = JobType.EVALUATION
    metrics: list[str] = ["meteor", "rouge", "bertscore", "bleu"]


class JobInferenceConfig(BaseModel):
    job_type: Literal[JobType.INFERENCE] = JobType.INFERENCE
    model: str
    provider: str
    task_definition: TaskDefinition = Field(default_factory=lambda: SummarizationTaskDefinition())
    accelerator: str | None = "auto"
    revision: str | None = "main"
    use_fast: bool = True  # Whether or not to use a Fast tokenizer if possible
    trust_remote_code: bool = False
    torch_dtype: str = "auto"
    base_url: str | None = None
    output_field: str | None = "predictions"
    max_tokens: int = 1024
    frequency_penalty: float = 0.0
    temperature: float = 1.0
    top_p: float = 1.0
    store_to_dataset: bool = False
    max_new_tokens: int = 500

    @model_validator(mode="after")
    def validate_and_set_defaults(self):
        # Text generation for causal models can mean anything
        # So we need to ensure the user provides a system prompt
        if self.task_definition.task == TaskType.TEXT_GENERATION and self.system_prompt is None:
            raise ValueError("system_prompt must be provided when task='text-generation'")

        # Set default system prompt if not provided
        if self.system_prompt is None:
            self.system_prompt = self._get_default_prompt()

        return self

    def _get_default_prompt(self) -> str:
        match self.task_definition.task:
            case TaskType.SUMMARIZATION:
                return DEFAULT_SUMMARIZATION_PROMPT
            case TaskType.TRANSLATION:
                return f"translate {self.task_definition.source_language} to {self.task_definition.target_language}:"


class JobAnnotateConfig(BaseModel):
    job_type: Literal[JobType.ANNOTATION] = JobType.ANNOTATION
    task: TaskType = Field(default=TaskType.SUMMARIZATION)
    store_to_dataset: bool = False


JobSpecificConfig = JobEvalConfig | JobInferenceConfig | JobAnnotateConfig
"""
Job configuration dealing exclusively with the Ray jobs
"""
# JobSpecificConfigVar = TypeVar('JobSpecificConfig', bound=JobSpecificConfig)
JobSpecificConfigVar = TypeVar("JobSpecificConfig", JobEvalConfig, JobInferenceConfig, JobAnnotateConfig)


class JobCreate(BaseModel):
    """Job configuration dealing exclusively with backend job handling"""

    name: str
    description: str = ""
    dataset: UUID
    max_samples: int = -1  # set to all samples by default
    job_config: JobSpecificConfig = Field(discriminator="job_type")


class JobAnnotateCreate(JobCreate):
    job_config: JobAnnotateConfig


class JobEvalCreate(JobCreate):
    job_config: JobEvalConfig


class JobInferenceCreate(JobCreate):
    job_config: JobInferenceConfig


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
    metrics: dict | None = {}
    parameters: dict | None = {}
    artifacts: dict | None = {}


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
