from pydantic import computed_field
from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL

from mzai.schemas.extras import DeploymentType


class BackendSettings(BaseSettings):
    DEPLOYMENT_TYPE: DeploymentType = DeploymentType.LOCAL

    # Postgres
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None

    # AWS
    AWS_HOST: str = "localhost"
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"
    AWS_DEFAULT_REGION: str = "us-east-2"
    S3_PORT: int = 4566
    S3_BUCKET: str = "platform-storage"

    # Ray
    RAY_HEAD_NODE_HOST: str = "localhost"
    RAY_DASHBOARD_PORT: int = 8265

    @computed_field
    @property
    def RAY_DASHBOARD_URL(self) -> str:  # noqa: N802
        return f"http://{self.RAY_HEAD_NODE_HOST}:{self.RAY_DASHBOARD_PORT}"

    @computed_field
    @property
    def S3_ENDPOINT_URL(self) -> str:  # noqa: N802
        return f"http://{self.AWS_HOST}:{self.RAY_DASHBOARD_PORT}"

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
