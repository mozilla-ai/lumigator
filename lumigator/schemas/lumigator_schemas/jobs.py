import datetime as dt
import json
import re
import uuid
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
        """Pre-processes and validates the 'entrypoint' configuration before model validation.

        This method uses Pydantic's 'model_validator' hook to parse the 'entrypoint'
        configuration, and where appropriate, redact sensitive information. It then
        assigns the processed configuration to the `config` field of the model
        (`JobSubmissionResponse`) before model validation occurs.

        :param values: The dictionary of field values to be processed.
            It contains the model data, including the 'entrypoint' configuration.
        :returns (dict[str, Any]): The updated values dictionary, with the processed
            'entrypoint' configuration assigned to the `config` field.
        """
        entrypoint = values.get(cls._entrypoint_key, None)

        if not isinstance(entrypoint, str):
            return values

        parsed_entrypoint = cls._parse_entrypoint(entrypoint)
        if parsed_entrypoint and cls.redactor is not None:
            values[cls._config_key] = cls.redactor.redact(parsed_entrypoint)

        return values

    @classmethod
    def _parse_entrypoint(cls, entrypoint: str) -> dict[str, Any] | None:
        """Parses the entrypoint string and extracts the configuration as a JSON object.

        This method processes the entrypoint string, extracting the associated JSON
        object (from Ray) using a specified flag.

        It further processes the extracted JSON to populate it with additional dataset information,
        sample limits, and model name or path, as required for further processing.

        :param entrypoint: The entrypoint string that contains the configuration.
            This string is parsed to extract the configuration in JSON format.
        :returns (dict[str, Any] | None): A dictionary representing the parsed configuration
            if successful, or None if no valid configuration could be extracted.
        """
        # Extract JSON for the specified flag.
        json_object = cls._extract_json_token(split(entrypoint), cls._config_flag)
        if not json_object:
            return None

        json_object["dataset"] = cls._extract_dataset(json_object)
        json_object["max_samples"] = cls._extract_max_samples(json_object)
        json_object["model_name_or_path"] = cls._extract_model_name_or_path(json_object)

        return json_object

    @classmethod
    def _extract_json_token(cls, tokens: list[str], flag: str) -> dict[str, Any] | None:
        """Extracts the token from the list following on from the specified flag and parses it as JSON.

        This method iterates through a list of tokens, finds the token that matches the given
        flag, and then extracts the next token as a JSON string. It attempts to parse the string
        as JSON and returns the resulting object. If no valid JSON token is found, or if the JSON
        parsing fails, it returns None.

        :param tokens: A list of tokens, where one of the tokens is expected to
            be a flag followed by a JSON-formatted string.
        :param flag: The flag used to identify the position of the desired JSON token in
            the token list.
        :returns (dict[str, Any] | None): A parsed JSON object if the JSON token is found and
            successfully parsed, or None if the token is not found or if parsing fails.
        """
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

    @classmethod
    def _extract_dataset(cls, config_dict: dict[str, Any]) -> dict[str, Any]:
        """Extracts the dataset ID and (file) name from the specified config dictionary.

        Retrieves the `dataset` path from the given config dictionary and attempts
        to extract the dataset ID (in UUID format) and the file name from the path. If the dataset
        path is missing or the UUID extraction fails, it raises a `ValueError`.

        :param config_dict: A dictionary containing the configuration data,
           which must include a "dataset" field with a "path" key.
        :returns (dict[str, Any]): A dictionary containing the extracted "id" (UUID) and
           "name" (file name) of the dataset.
        :raises ValueError: If the dataset path cannot be found or if the extracted dataset
           ID is not a valid UUID.
        """
        dataset_path = config_dict.get("dataset", {}).get("path", "")
        if not dataset_path:
            raise ValueError(f"Unable to parse dataset path from entrypoint config: {config_dict}")

        match = re.search(
            r".*/datasets/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/([^/]+)$", dataset_path, re.I
        )

        if not match:
            raise ValueError(f"Could not extract dataset ID and file name from path: {dataset_path}")

        dataset_id = match.group(1)
        file_name = match.group(2)

        try:
            dataset_uuid = uuid.UUID(dataset_id)
        except ValueError as e:
            raise ValueError(f"Extracted dataset ID '{dataset_id}' is not a valid UUID") from e

        return {"id": dataset_uuid, "name": file_name}

    @classmethod
    def _extract_model_name_or_path(cls, config_dict: dict[str, Any]) -> str | None:
        """Extract and normalize the model path or name from the given configuration dictionary.

        Retrieves the model name (or path) from various locations in the provided configuration.
        If no model path or name is found, it returns `None`.

        :param config_dict (dict[str, Any]): A dictionary containing the configuration data,
            which may include model information under different sections like `model`, `hf_pipeline`,
            or `inference_server`.
        :returns  (str | None): The model name or path if found, otherwise `None`.
        """
        # NOTE: Some jobs don't have models (e.g. evaluation).
        model_name_or_path = (
            config_dict.get("model", {}).get("path")
            or config_dict.get("model", {}).get("inference", {}).get("model")
            or config_dict.get("hf_pipeline", {}).get("model_name_or_path")
            or config_dict.get("inference_server", {}).get("model")
        )

        return model_name_or_path

    @classmethod
    def _extract_max_samples(cls, config_dict: dict[str, Any]) -> int:
        """Extract the `max_samples` value from the configuration dictionary in the `job` and `evaluation` entries.

        :param config_dict (dict[str, Any]): The configuration dictionary to extract `max_samples` from.
        :returns  (int): The value of `max_samples` if found.
        :raises ValueError: If `max_samples` is not found in the `job` or `evaluation` sections.
        """
        for key in ("job", "evaluation"):
            if (max_samples := config_dict.get(key, {}).get("max_samples")) is not None:
                return max_samples
        raise ValueError(f"Unable to parse max_samples from entrypoint config: {config_dict}")


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
