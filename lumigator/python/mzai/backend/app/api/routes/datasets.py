from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, UploadFile, status
from pydantic import BaseModel
from schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse
from schemas.extras import ListingResponse

from app.api.deps import DatasetServiceDep

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def upload_dataset(
    service: DatasetServiceDep,
    dataset: UploadFile,
    format: Annotated[DatasetFormat, Form()],
) -> DatasetResponse:
    return service.upload_dataset(dataset, format)


@router.get("/{dataset_id}")
def get_dataset(service: DatasetServiceDep, dataset_id: UUID) -> DatasetResponse:
    return service.get_dataset(dataset_id)


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(service: DatasetServiceDep, dataset_id: UUID) -> None:
    service.delete_dataset(dataset_id)


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
