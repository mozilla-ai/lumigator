from pydantic import BaseModel, Field

from src.settings import DeploymentType


class Health(BaseModel):
    deployment: DeploymentType = Field(..., example=DeploymentType.PRODUCTION)
    status: str = Field(..., example="Ok")
