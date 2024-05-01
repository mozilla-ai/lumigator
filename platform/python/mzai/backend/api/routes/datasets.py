from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, UploadFile

from mzai.backend.api.deps import ContentLengthDep, DatasetServiceDep
from mzai.schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse
from mzai.schemas.extras import ListingResponse

router = APIRouter()


@router.post("/", dependencies=[ContentLengthDep])
def upload_dataset(
    service: DatasetServiceDep,
    dataset: UploadFile,
    format: Annotated[DatasetFormat, Form()],
) -> DatasetResponse:
    return service.upload_dataset(dataset, format)


@router.get("/{dataset_id}")
def get_dataset(service: DatasetServiceDep, dataset_id: UUID) -> DatasetResponse:
    return service.get_dataset(dataset_id)


@router.get("/")
def list_datasets(
    service: DatasetServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[DatasetResponse]:
    return service.list_datasets(skip, limit)


@router.get("/{dataset_id}/download")
def get_dataset_download(service: DatasetServiceDep, dataset_id: UUID) -> DatasetDownloadResponse:
    return service.get_dataset_download(dataset_id)
