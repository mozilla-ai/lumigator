from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, UploadFile

from mzai.backend.api.deps import DatasetServiceDep
from mzai.schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse
from mzai.schemas.extras import ListingResponse

router = APIRouter()


@router.post("/")
def upload_dataset(
    service: DatasetServiceDep,
    dataset: UploadFile,
    format: Annotated[DatasetFormat, Form()],
) -> DatasetResponse:
    return service.upload_dataset(dataset, format)


@router.get("/{dataset_id}")
def get_dataset(service: DatasetServiceDep, dataset_id: UUID) -> DatasetResponse:
    pass


@router.get("/")
def list_experiments(
    service: DatasetServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[DatasetResponse]:
    pass


@router.get("/{dataset_id}/contents")
def get_dataset_contents(service: DatasetServiceDep, dataset_id: UUID) -> DatasetDownloadResponse:
    pass
