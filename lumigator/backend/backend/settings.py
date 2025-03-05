import os
import re
from collections.abc import Mapping
from enum import Enum
from typing import Final

from lumigator_schemas.extras import DeploymentType
from pydantic import ByteSize, computed_field
from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL, make_url


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
        re.compile(r"(?i)_api_key"),  # Matches fields like OPENAI_API_KEY, MISTRAL_API_KEY etc.
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

    def inherit_ray_env(self, runtime_env_vars: Mapping[str, str]):
        for env_var_name in self.RAY_WORKER_ENV_VARS:
            env_var = os.environ.get(env_var_name, None)
            if env_var is not None:
                runtime_env_vars[env_var_name] = env_var

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


settings = BackendSettings()
