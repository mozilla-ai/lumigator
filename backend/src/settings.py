from enum import Enum

from pydantic import computed_field
from pydantic_core import Url
from pydantic_settings import BaseSettings


class DeploymentType(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    DEPLOYMENT_TYPE: DeploymentType = DeploymentType.LOCAL

    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int | None = None
    POSTGRES_DB: str | None = None

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> Url:  # noqa: N802
        if self.DEPLOYMENT_TYPE == DeploymentType.LOCAL:
            # In-memory SQLite connection when running locally without PG
            return Url.build(scheme="sqlite", host="")
        else:
            return Url.build(
                scheme="postgresql",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )


settings = Settings()
