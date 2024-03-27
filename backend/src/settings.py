from enum import Enum

from pydantic import computed_field
from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL


class DeploymentType(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    DEPLOYMENT_TYPE: DeploymentType = DeploymentType.LOCAL

    # Postgres
    POSTGRES_PORT: int = 5432
    POSTGRES_HOST: str = "localhost"
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None

    # Ray
    RAY_HEAD_NODE_IP: str = "10.147.62.75"
    RAY_HEAD_NODE_PORT: int = 8265

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> URL:  # noqa: N802
        return URL.create(
            drivername="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        )


settings = Settings()
