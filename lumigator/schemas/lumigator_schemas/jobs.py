import datetime as dt
from enum import Enum
from typing import Any, Literal, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from lumigator_schemas.redactable_base_model import RedactableBaseModel
from lumigator_schemas.tasks import (
    SummarizationTaskDefinition,
    TaskDefinition,
    TaskType,
)
from lumigator_schemas.transforms.job_submission_response_transform import transform_job_submission_response


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
    STOPPED = "stopped"


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
class JobSubmissionResponse(RedactableBaseModel):
    type: str | None = None
    submission_id: str | None = None
    driver_info: str | None = None
    status: str | None = None
    config: dict | None = Field(default_factory=dict)
    message: str | None = None
    error_type: str | None = None
    start_time: dt.datetime | None = None
    end_time: dt.datetime | None = None
    metadata: dict = Field(default_factory=dict)
    runtime_env: dict = Field(default_factory=dict)
    driver_agent_http_address: str | None = None
    driver_node_id: str | None = None
    driver_exit_code: int | None = None

    @model_validator(mode="before")
    @classmethod
    def transform(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Pre-processes and validates the 'entrypoint' configuration before model validation.

        This method uses Pydantic's 'model_validator' hook to parse the 'entrypoint'
        configuration, and where appropriate, redact sensitive information. It then
        assigns the processed configuration to the `config` field of the model
        (`JobSubmissionResponse`) before model validation occurs.

        :param values: The dictionary of field values to be processed.
            It contains the model data, including the 'entrypoint' configuration.
        :return: The updated values dictionary, with the processed and
            potentially redacted 'entrypoint' configuration assigned to the `config` field.
        """
        transformed_values = transform_job_submission_response(values)
        return transformed_values


class JobEvalConfig(BaseModel):
    job_type: Literal[JobType.EVALUATION] = JobType.EVALUATION
    metrics: list[str] = ["rouge", "meteor", "bertscore", "bleu"]


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
    max_new_tokens: int = 1024
    frequency_penalty: float = 0.0
    temperature: float = 1.0
    top_p: float = 1.0
    store_to_dataset: bool = False
    system_prompt: str | None = Field(
        title="System Prompt",
        description="System prompt to use for the model inference."
        "If not provided, a task-specific default prompt will be used.",
        default=None,
        examples=[
            "You are an advanced AI trained to summarize documents accurately and concisely. "
            "Your goal is to extract key information while maintaining clarity and coherence."
        ],
    )


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
