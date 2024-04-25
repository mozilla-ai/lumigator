from pydantic_settings import BaseSettings


class JoblibSettings(BaseSettings):
    BACKEND_HOST: str = "localhost"
    BACKEND_PORT: int = 80


settings = JoblibSettings()
