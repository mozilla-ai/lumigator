import os
from collections.abc import Mapping

from lumigator_schemas.extras import DeploymentType
from pydantic import ByteSize, computed_field
from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL, make_url


class BackendSettings(BaseSettings):
    # Backend
    DEPLOYMENT_TYPE: DeploymentType = DeploymentType.LOCAL
    MAX_DATASET_SIZE: ByteSize = "50MB"

    # Backend API env vars
    _api_cors_allowed_origins: str = os.environ.get("LUMI_API_CORS_ALLOWED_ORIGINS", "")

    # Postgres
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None

    # AWS
    S3_ENDPOINT_URL: str | None = None
    S3_BUCKET: str = "lumigator-storage"
    S3_URL_EXPIRATION: int = 3600  # Time in seconds for pre-signed url expiration
    S3_DATASETS_PREFIX: str = "datasets"
    S3_JOB_RESULTS_PREFIX: str = "jobs/results"
    S3_JOB_RESULTS_FILENAME: str = "{job_name}/{job_id}/eval_results.json"

    # Ray
    RAY_HEAD_NODE_HOST: str = "localhost"
    RAY_DASHBOARD_PORT: int = 8265
    RAY_SERVE_INFERENCE_PORT: int = 8000
    # the following vars will be copied, if present, from Ray head to workers
    # Secrets should be added directly to ray by setting env vars on the ray head/worker nodes
    RAY_WORKER_ENV_VARS: list[str] = []
    RAY_WORKER_GPUS_ENV_VAR: str = "RAY_WORKER_GPUS"
    RAY_WORKER_GPUS_FRACTION_ENV_VAR: str = "RAY_WORKER_GPUS_FRACTION"

    # Served models
    OAI_API_URL: str = "https://api.openai.com/v1"
    MISTRAL_API_URL: str = "https://api.mistral.ai/v1"
    DEFAULT_SUMMARIZER_PROMPT: str = "You are a helpful assistant, expert in text summarization. For every prompt you receive, provide a summary of its contents in at most two sentences."  # noqa: E501

    # Eval job details
    EVALUATOR_WORK_DIR: str | None = None
    EVALUATOR_PIP_REQS: str | None = None

    @computed_field
    @property
    def EVALUATOR_COMMAND(self) -> str:  # noqa: N802
        """Returns the command required to run evaluator.

        The prefix is provided to fix an issue loading libgomp (an sklearn dependency)
        on the aarch64 ray image (see LD_PRELOAD_PREFIX definition below for more details)
        """
        return f"{self.LD_PRELOAD_PREFIX} python -m evaluator evaluate huggingface"

    # Inference job details
    INFERENCE_WORK_DIR: str | None = None
    INFERENCE_PIP_REQS: str | None = None
    INFERENCE_COMMAND: str = "python inference.py"

    def inherit_ray_env(self, runtime_env_vars: Mapping[str, str]):
        for env_var_name in self.RAY_WORKER_ENV_VARS:
            env_var = os.environ.get(env_var_name, None)
            if env_var is not None:
                runtime_env_vars[env_var_name] = env_var

    OAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")

    MISTRAL_API_KEY: str = os.environ.get("MISTRAL_API_KEY", "")

    @computed_field
    @property
    def LD_PRELOAD_PREFIX(self) -> str:  # noqa: N802
        """Sets the LD_PRELOAD env var for aarch64.

        The ray image on Mac has a known issue ("cannot allocate memory in static TLS block")
        loading libgomp (see https://github.com/mozilla-ai/lumigator/issues/156).
        To fix this we preload the library adding it to the LD_PRELOAD env variable.
        As the path is relative to ray workers' virtual environment, we set this variable
        right before calling the job command by prepending it to the command itself.
        """
        lib_path = "lib/python3.11/site-packages/scikit_learn.libs/libgomp-d22c30c5.so.1.0.0"

        # We set the LD_PRELOAD env var ONLY if the architecture is aarch64.
        # NOTE that we are using POSIX compliant commands (e.g. "=" instead of "==")
        # as the default shell in the container is /bin/sh
        return f'if [ `arch` = "aarch64" ]; then export LD_PRELOAD=$VIRTUAL_ENV/{lib_path}; fi;'

    # URL for Ray jobs API
    @computed_field
    @property
    def RAY_VERSION_URL(self) -> str:  # noqa: N802
        return f"{self.RAY_DASHBOARD_URL}/api/version"

    @computed_field
    @property
    def RAY_WORKER_GPUS(self) -> float:  # noqa: N802
        return float(os.environ.get(self.RAY_WORKER_GPUS_ENV_VAR, 1.0))

    @computed_field
    @property
    def RAY_WORKER_GPUS_FRACTION(self) -> float:  # noqa: N802
        return float(os.environ.get(self.RAY_WORKER_GPUS_FRACTION_ENV_VAR, 1.0))

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
