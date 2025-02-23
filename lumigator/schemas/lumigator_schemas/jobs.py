import datetime as dt
import json
import re
from enum import Enum
from itertools import dropwhile
from json import JSONDecodeError
from shlex import split
from typing import Any, ClassVar, Literal, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from lumigator_schemas.redactable_base_model import RedactableBaseModel

from lumigator_schemas.tasks import (
    SummarizationTaskDefinition,
    TaskDefinition,
    TaskType,
)


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

    # Key used to identify the entrypoint in data sent to Ray.
    _entrypoint_key: ClassVar[str] = "entrypoint"

    # Flag used to indicate 'config' in the entrypoint sent to Ray.
    _config_flag: ClassVar[str] = "--config"

    # Key used to identify config on the JobSubmission model.
    _config_key: ClassVar[str] = "config"

    @model_validator(mode="before")
    @classmethod
    def parse(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Normalize and redact 'entrypoint' field before model validation."""
        entrypoint = values.get(cls._entrypoint_key, None)

        if not isinstance(entrypoint, str):
            return values

        parsed_entrypoint = cls.parse_entrypoint(entrypoint)
        if parsed_entrypoint and cls.redactor is not None:
            values[cls._config_key] = cls.redactor.redact(parsed_entrypoint)

        return values

    @staticmethod
    def extract_json_token(tokens: list[str], flag: str) -> dict[str, Any] | None:
        """Extract the token following the flag and parse it as JSON."""
        # Drop tokens until we reach the flag
        token_iter = dropwhile(lambda t: t != flag, tokens)
        next(token_iter, None)  # Consume the flag itself
        config_json = next(token_iter, None)  # Get the actual config JSON

        if not config_json:
            return None

        # Remove potential wrapping single quotes.
        config_json = config_json.strip().lstrip("'").rstrip("'")

        try:
            return json.loads(config_json)
        except JSONDecodeError:
            return None

    @staticmethod
    def extract_model_name_or_path(json_object: dict[str, Any]) -> str | None:
        """Extract and normalize the model path from the given JSON object."""
        model_name_or_path = (
            json_object.get("model", {}).get("path")
            or json_object.get("model", {}).get("inference", {}).get("model")
            or json_object.get("hf_pipeline", {}).get("model_name_or_path")
            or json_object.get("inference_server", {}).get("model")
        )

        return model_name_or_path

    @classmethod
    def parse_entrypoint(cls, entrypoint: str) -> dict[str, Any] | None:
        """Parse the entrypoint string and extract the config JSON."""
        tokens = split(entrypoint)

        # Extract JSON for the specified flag.
        json_object = cls.extract_json_token(tokens, cls._config_flag)
        if not json_object:
            return None

        # Normalize dataset field
        dataset_match = re.search(r"datasets/([^/]+)/([^/]+)", json_object.get("dataset", {}).get("path", ""))
        if dataset_match:
            json_object["dataset"] = {"id": dataset_match.group(1), "name": dataset_match.group(2)}

        # Normalize job max_samples field
        json_object["max_samples"] = json_object.get("job", {}).get("max_samples") or json_object.get(
            "evaluation", {}
        ).get("max_samples")

        if json_object["max_samples"] is None:
            raise ValueError(f"Unable to parse max_samples from entrypoint config: {json_object}")

        # Some jobs don't have models attached (e.g. evaluation).
        model_path = cls.extract_model_name_or_path(json_object)

        json_object.setdefault("model", {})["path"] = model_path

        return json_object


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
