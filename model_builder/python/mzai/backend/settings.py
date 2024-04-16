from enum import Enum

from pydantic import SecretStr
from pydantic_settings import BaseSettings
from sqlalchemy.engine import URL


class DeploymentType(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    # Backend
    DEPLOYMENT_TYPE: DeploymentType = DeploymentType.LOCAL

    # Postgres
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: SecretStr | None = None
    POSTGRES_DB: str | None = None

    # RabbitMQ
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672

    # Ray
    RAY_HEAD_NODE_HOST: str = "localhost"
    RAY_DASHBOARD_PORT: int = 8265

    @property
    def RAY_DASHBOARD_URL(self) -> str:  # noqa: N802
        return f"http://{self.RAY_HEAD_NODE_HOST}:{self.RAY_DASHBOARD_PORT}"

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> URL:  # noqa: N802
        return URL.create(
            drivername="postgresql",
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD.get_secret_value() if self.POSTGRES_PASSWORD else None,
            database=self.POSTGRES_DB,
        )


settings = Settings()
