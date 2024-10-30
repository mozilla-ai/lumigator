from typing import Annotated
from uuid import UUID

import loguru
from fastapi import APIRouter, Form, HTTPException, UploadFile, status
from schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse
from schemas.extras import ListingResponse

from backend.api.deps import DatasetServiceDep

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
    try:
        service.delete_dataset(dataset_id)
    except Exception as e:
        loguru.logger.error(f"Unexpected error deleting dataset ID from DB and S3: {dataset_id}. "
                            f"{e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error deleting data for ID: {dataset_id}",
        ) from e


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
