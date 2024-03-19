from pydantic import BaseModel, Field

from src.settings import EnvironmentType
from enum import Enum


class Health(BaseModel):
    environment: EnvironmentType = Field(..., example=EnvironmentType.PRODUCTION)
    status: str = Field(..., example="Healthy")

class StatusEnum(str, Enum):
    started = "STARTED" 
    cancelled = "PENDING"  
    finished = "FINISHED"

class Status(BaseModel):
    id: str
    model: str
    status: StatusEnum
    
