import datetime
from enum import Enum
from uuid import UUID

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.api.deps import ExperimentServiceDep


class JobStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    FAILED = "failed"
    SUCCEEDED = "succeeded"


from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel

ItemType = TypeVar("ItemType")
# from mzai.schemas.experiments import (
#     ExperimentCreate,
#     ExperimentResponse,
#     ExperimentResultDownloadResponse,
#     ExperimentResultResponse,
# )
# from mzai.schemas.extras import ListingResponse


class ListingResponse(BaseModel, Generic[ItemType]):
    total: int
    items: list[ItemType]


router = APIRouter()


class ExperimentCreate(BaseModel):
    name: str
    description: str = ""
    model: str
    dataset: UUID
    max_samples: int | None = None
    model_url: str | None = None
    system_prompt: str | None = None
    config_template: str | None = None


class ExperimentResponse(BaseModel, from_attributes=True):
    id: UUID
    name: str
    description: str
    status: JobStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime | None


class ExperimentResultResponse(BaseModel, from_attributes=True):
    id: UUID
    experiment_id: UUID


class ExperimentResultDownloadResponse(BaseModel):
    id: UUID
    download_url: str


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_experiment(
    service: ExperimentServiceDep,
    request: ExperimentCreate,
) -> ExperimentResponse:
    return service.create_experiment(request)


@router.get("/{experiment_id}")
def get_experiment(service: ExperimentServiceDep, experiment_id: UUID) -> ExperimentResponse:
    return service.get_experiment(experiment_id)


@router.get("/")
def list_experiments(
    service: ExperimentServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[ExperimentResponse]:
    return service.list_experiments(skip, limit)


@router.get("/{experiment_id}/result")
def get_experiment_result(
    service: ExperimentServiceDep,
    experiment_id: UUID,
) -> ExperimentResultResponse:
    """Return experiment results metadata if available in the DB."""
    return service.get_experiment_result(experiment_id)


@router.get("/{experiment_id}/result/download")
def get_experiment_result_download(
    service: ExperimentServiceDep,
    experiment_id: UUID,
) -> ExperimentResultDownloadResponse:
    """Return experiment results file URL for downloading."""
    return service.get_experiment_result_download(experiment_id)
