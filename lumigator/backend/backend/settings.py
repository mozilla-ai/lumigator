import os
import re
import tomllib
from collections.abc import Mapping
from enum import Enum
from pathlib import Path
from typing import Final

from lumigator_schemas.extras import DeploymentType
from lumigator_schemas.tasks import TaskDefinition, TaskType
from pydantic import ByteSize, computed_field
from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL, make_url

SUMMARIZATION_SYSTEM_PROMPT_DEFAULT: str = (
    "You are a helpful assistant, expert in text summarization. "
    "For every prompt you receive, provide a summary of its contents in at most two sentences."
)

TRANSLATION_SYSTEM_PROMPT_DEFAULT: str = (
    "You are a helpful assistant, expert in text translation. For every prompt you recieve, translate {0} to {1}."
)

SYSTEM_PROMPT_DEFAULTS: dict = {
    TaskType.SUMMARIZATION: SUMMARIZATION_SYSTEM_PROMPT_DEFAULT,
    TaskType.TRANSLATION: lambda task_definition: TRANSLATION_SYSTEM_PROMPT_DEFAULT.format(
        task_definition.source_language, task_definition.target_language
    ),
}


class BackendSettings(BaseSettings):
    # Backend
    LUMIGATOR_SECRET_KEY: str  # Symmetric encryption key used for interacting with stored secrets
    DEPLOYMENT_TYPE: DeploymentType = DeploymentType.LOCAL
    MAX_DATASET_SIZE_HUMAN_READABLE: Final[str] = "50MB"
    MAX_DATASET_SIZE: ByteSize = MAX_DATASET_SIZE_HUMAN_READABLE

    # Backend API env vars
    _api_cors_allowed_origins: str = os.environ.get("LUMIGATOR_API_CORS_ALLOWED_ORIGINS", "")

    # AWS
    S3_ENDPOINT_URL: str | None = None
    S3_BUCKET: str  # Default is specified in .env file
    S3_URL_EXPIRATION: int = 3600  # Time in seconds for pre-signed url expiration
    S3_DATASETS_PREFIX: str = "datasets"
    S3_JOB_RESULTS_PREFIX: str = "jobs/results"
    S3_JOB_RESULTS_FILENAME: str = "{job_name}/{job_id}/results.json"

    # Ray
    RAY_HEAD_NODE_HOST: str  # Default is specified in .env file
    RAY_DASHBOARD_PORT: int  # Default is specified in .env file
    RAY_SERVE_INFERENCE_PORT: int = 8000
    # the following vars will be copied, if present, from Ray head to workers
    # Secrets should be added directly to ray by setting env vars on the ray head/worker nodes
    RAY_WORKER_ENV_VARS: list[str] = []
    RAY_WORKER_GPUS_ENV_VAR: str = "RAY_WORKER_GPUS"
    RAY_WORKER_GPUS_FRACTION_ENV_VAR: str = "RAY_WORKER_GPUS_FRACTION"

    # Sensitive data patterns for redaction
    sensitive_patterns: list[re.Pattern] = [
        re.compile(r"(?i)api_key"),  # Matches fields like OPENAI_API_KEY, MISTRAL_API_KEY etc.
        re.compile(r"(?i)_token"),  # Matches fields like access_token, HF_TOKEN etc.
    ]

    # Tracking
    class TrackingBackendType(str, Enum):
        """Enum for tracking backend types."""

        MLFLOW = "mlflow"

    TRACKING_BACKEND: TrackingBackendType = TrackingBackendType.MLFLOW

    @computed_field
    @property
    # Default is specified in .env file
    def TRACKING_BACKEND_URI(self) -> str:  # noqa: N802
        if self.TRACKING_BACKEND == self.TrackingBackendType.MLFLOW:
            # the tracking uri env var must be set, return that
            tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")
            if not tracking_uri:  # This catches both None and empty strings
                raise ValueError("MLFLOW_TRACKING_URI environment variable must be set to a valid URI")
            return tracking_uri
        raise ValueError(f"Unsupported tracking backend: {self.TRACKING_BACKEND}")

    # Served models
    OAI_API_URL: str = "https://api.openai.com/v1"
    MISTRAL_API_URL: str = "https://api.mistral.ai/v1"
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1"

    def with_ray_worker_env_vars(self, runtime_env_vars: Mapping[str, str]) -> dict[str, str]:
        """Takes a mapping of runtime environment variables and merges it with environment
        variables defined in ``RAY_WORKER_ENV_VARS``. If any of these predefined variables already exist
        in the input mapping, the values from the environment will be preferred (if they exist).

        :param runtime_env_vars: An immutable mapping of environment variables (key-value pairs) to be augmented
        :returns: A dictionary containing the merged environment variables
        """
        # Start with a copy of the input environment variables.
        merged_env_vars = dict(**runtime_env_vars)

        # Add/update environment variables from RAY_WORKER_ENV_VARS if they exist
        for var_name in self.RAY_WORKER_ENV_VARS:
            if (env_value := os.getenv(var_name)) is not None:
                merged_env_vars[var_name] = env_value

        return merged_env_vars

    def get_default_system_prompt(self, task_definition: TaskDefinition) -> str:
        generator = SYSTEM_PROMPT_DEFAULTS.get(task_definition.task)
        if not generator:
            raise ValueError(
                f"Default system_prompt not available for {task_definition.task.value}. "
                "It must be provided explicitly by the user."
            )

        return generator(task_definition) if callable(generator) else generator

    # URL for Ray jobs API
    @computed_field
    @property
    def RAY_VERSION_URL(self) -> str:  # noqa: N802
        return f"{self.RAY_DASHBOARD_URL}/api/version"

    @computed_field
    @property
    def RAY_WORKER_GPUS(self) -> float:  # noqa: N802
        return float(os.environ.get(self.RAY_WORKER_GPUS_ENV_VAR) or 1.0)

    @computed_field
    @property
    def RAY_WORKER_GPUS_FRACTION(self) -> float:  # noqa: N802
        return float(os.environ.get(self.RAY_WORKER_GPUS_FRACTION_ENV_VAR) or 1.0)

    # URL for the Ray Dashboard
    @computed_field
    @property
    def RAY_DASHBOARD_URL(self) -> str:  # noqa: N802
        return f"http://{self.RAY_HEAD_NODE_HOST}:{self.RAY_DASHBOARD_PORT}"

    # URL for Ray jobs API
    @computed_field
    @property
    def RAY_JOBS_URL(self) -> str:  # noqa: N802
        return f"{self.RAY_DASHBOARD_URL}/api/jobs/"

    # URL for the DB used by Alchemy, please refer to
    # https://docs.sqlalchemy.org/en/20/core/engines.html#backend-specific-urls
    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> URL:  # noqa: N802
        return make_url(os.environ.get("SQLALCHEMY_DATABASE_URL", None))

    @computed_field
    @property
    def API_CORS_ALLOWED_ORIGINS(self) -> list[str]:  # noqa: N802
        """Retrieves the (comma separated) list of allowed origin URLs for CORS requests
        against the Lumigator backend API.

        If the wildcard '*' appears as an origin, only it will be returned, ignoring other origins.
        """
        wildcard = "*"
        result = []
        origins = self._api_cors_allowed_origins.strip()

        # Return early if there are no origin settings.
        if origins == "":
            return result

        for origin in origins.split(","):
            o = origin.strip()
            if o == wildcard:
                # Return only the wildcard if we encountered it, as the other settings are moot.
                return [o]
            if o != "":
                result.append(o)

        return result

    @computed_field
    @property
    def PROJECT_ROOT(self) -> Path:  # noqa: N802
        """Returns the root path of the Lumigator backend project."""
        return Path(__file__).resolve().parent.parent

    @computed_field
    @property
    def VERSION(self) -> str:  # noqa: N802
        """Returns the version of the Lumigator backend."""
        try:
            with Path.open(Path(self.PROJECT_ROOT / "pyproject.toml"), "rb") as f:
                data = tomllib.load(f)
            return data["project"]["version"]
        except Exception as e:
            raise RuntimeError("Unable to retrieve Lumigator backend version.") from e


settings = BackendSettings()
