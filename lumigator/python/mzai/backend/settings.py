from pydantic import ByteSize, computed_field
from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL

from mzai.schemas.extras import DeploymentType


class BackendSettings(BaseSettings):
    # Backend
    DEPLOYMENT_TYPE: DeploymentType = DeploymentType.LOCAL
    MAX_DATASET_SIZE: ByteSize = "50MB"

    # Postgres
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None

    # AWS
    AWS_HOST: str | None = None
    S3_PORT: int = 4566
    S3_BUCKET: str = "lumigator-storage"
    S3_URL_EXPIRATION: int = 3600  # Time in seconds for pre-signed url expiration
    S3_DATASETS_PREFIX: str = "datasets"
    S3_EXPERIMENT_RESULTS_PREFIX: str = "experiments/results"
    S3_EXPERIMENT_RESULTS_FILENAME: str = "{experiment_name}/{experiment_id}/eval_results.json"

    # Ray
    RAY_HEAD_NODE_HOST: str = "localhost"
    RAY_DASHBOARD_PORT: int = 8265
    RAY_SERVE_INFERENCE_PORT: int = 8000
    # the following vars will be copied, if present, from Ray head to workers
    RAY_WORKER_ENV_VARS: list[str] = [
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_ENDPOINT_URL",
        "AWS_HOST",
        "LOCAL_FSSPEC_S3_KEY",
        "LOCAL_FSSPEC_S3_SECRET",
        "LOCAL_FSSPEC_S3_ENDPOINT_URL",
        "HF_TOKEN",
        "OPENAI_API_KEY",
        "MISTRAL_API_KEY",
    ]
    RAY_WORKER_GPUS_ENV_VAR: str = "RAY_WORKER_GPUS"
    RAY_WORKER_GPUS_FRACTION_ENV_VAR: str = "RAY_WORKER_GPUS_FRACTION"

    # Served models
    OAI_API_URL: str = "https://api.openai.com/v1"
    MISTRAL_API_URL: str = "https://api.mistral.ai/v1"
    DEFAULT_SUMMARIZER_PROMPT: str = "You are a helpful assistant, expert in text summarization. For every prompt you receive, provide a summary of its contents in at most two sentences."  # noqa: E501

    # Summarizer
    SUMMARIZER_WORK_DIR: str | None = None

    @computed_field
    @property
    def S3_ENDPOINT_URL(self) -> str | None:  # noqa: N802
        # Live AWS doesn't require this but LocalStack testing does, so it's optional
        if self.AWS_HOST == "localstack":
            return f"http://{self.AWS_HOST}:{self.S3_PORT}"

    @computed_field
    @property
    def RAY_DASHBOARD_URL(self) -> str:  # noqa: N802
        return f"http://{self.RAY_HEAD_NODE_HOST}:{self.RAY_DASHBOARD_PORT}"

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> URL:  # noqa: N802
        return URL.create(
            drivername="postgresql",
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            database=self.POSTGRES_DB,
        )


settings = BackendSettings()
