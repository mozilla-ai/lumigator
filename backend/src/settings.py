from enum import Enum

from pydantic_settings import BaseSettings


class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: EnvironmentType = EnvironmentType.DEVELOPMENT


settings = Settings()
