from uuid import UUID

from pydantic import BaseModel, Field

from src.schemas.extras import JobStatus


class FinetuningJobCreate(BaseModel):
    name: str
    config: dict = Field(default_factory=dict)


class FinetuningJobResponse(BaseModel, from_attributes=True):
    id: UUID
    name: str
    status: JobStatus


class ListFinetuningJobs(BaseModel):
    count: int
    jobs: list[FinetuningJobResponse]
