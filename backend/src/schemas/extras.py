from pydantic import BaseModel, Field

from src.settings import EnvironmentType


class Health(BaseModel):
    environment: EnvironmentType = Field(..., example=EnvironmentType.PRODUCTION)
    status: str = Field(..., example="Healthy")