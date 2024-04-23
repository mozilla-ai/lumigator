from uuid import UUID

from pydantic import BaseModel

from mzai.schemas.extras import JobStatus


class ExperimentCreate(BaseModel):
    name: str
    description: str = ""


class ExperimentResponse(BaseModel, from_attributes=True):
    id: UUID
    name: str
    description: str
    status: JobStatus


class ExperimentResultResponse(BaseModel, from_attributes=True):
    pass
