from pydantic import computed_field
from pydantic_settings import BaseSettings


class JobRunnerSettings(BaseSettings):
    BACKEND_HOST: str = "localhost"
    BACKEND_PORT: int = 80

    @computed_field
    @property
    def BACKEND_EVENTS_URL(self) -> str:  # noqa: N802
        return f"http://{self.BACKEND_HOST}:{self.BACKEND_PORT}/api/v1/events"


settings = JobRunnerSettings()
