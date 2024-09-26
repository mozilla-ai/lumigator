import datetime
from enum import Enum
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, UploadFile, status

# from mzai.schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse
# from mzai.schemas.extras import ListingResponse
from pydantic import BaseModel

from app.api.deps import DatasetServiceDep

router = APIRouter()

from typing import Generic, TypeVar

from pydantic import BaseModel

ItemType = TypeVar("ItemType")


class DatasetFormat(str, Enum):
    EXPERIMENT = "experiment"


class DatasetDownloadResponse(BaseModel):
    id: UUID
    download_urls: list[str]


class DatasetResponse(BaseModel, from_attributes=True):
    id: UUID
    filename: str
    format: DatasetFormat
    size: int
    created_at: datetime.datetime


@router.post("/", status_code=status.HTTP_201_CREATED)
def upload_dataset(
    service: DatasetServiceDep,
    dataset: UploadFile,
    format: Annotated[DatasetFormat, Form()],
) -> DatasetResponse:
    return service.upload_dataset(dataset, format)


class ListingResponse(BaseModel, Generic[ItemType]):
    total: int
    items: list[ItemType]


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
