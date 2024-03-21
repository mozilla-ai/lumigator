from pydantic import BaseModel, Field

from src.settings import DeploymentType


class Health(BaseModel):
    status: str = Field(..., example="Ok")
    deployment_type: DeploymentType = Field(..., example=DeploymentType.PRODUCTION)
