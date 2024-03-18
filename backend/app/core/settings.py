from pathlib import Path

from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    RAY_HEAD_NODE_IP: str = "10.147.62.75"
    RAY_HEAD_NODE_PORT: int = 8265
    SQLALCHEMY_DATABASE_URI: MultiHostUrl = MultiHostUrl.build(
        scheme="sqlite+aiosqlite",
        host="",
        path=str(Path(__file__).parents[1] / "database.db"),
    )


settings = Settings()
