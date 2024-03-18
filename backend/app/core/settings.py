from enum import Enum

from pydantic_settings import BaseSettings


class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    RAY_HEAD_NODE_IP: str = "10.147.62.75"
    RAY_HEAD_NODE_PORT: int = 8265
    ENVIRONMENT: EnvironmentType = EnvironmentType.DEVELOPMENT


settings = Settings()
