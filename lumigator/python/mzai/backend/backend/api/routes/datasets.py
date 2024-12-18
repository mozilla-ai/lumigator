from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, HTTPException, UploadFile, status
from loguru import logger
from lumigator_schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse
from lumigator_schemas.extras import ListingResponse
from starlette.requests import Request
from starlette.responses import Response

from backend.api.deps import DatasetServiceDep
from backend.api.http_headers import HttpHeaders

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def upload_dataset(
    service: DatasetServiceDep,
    dataset: UploadFile,
    format: Annotated[DatasetFormat, Form()],
    request: Request,
    response: Response,
    run_id: Annotated[
        UUID | None, Form(description="Provide the Jod ID that generated this dataset.")
    ] = None,
    generated: Annotated[bool, Form(description="Is the dataset is AI-generated?")] = False,
    generated_by: Annotated[
        str | None, Form(description="The name of the AI model that generated this dataset.")
    ] = None,
) -> DatasetResponse:
    ds_response = service.upload_dataset(
        dataset, format, run_id=run_id, generated=generated, generated_by=generated_by
    )

    url = request.url_for(get_dataset.__name__, dataset_id=ds_response.id)
    response.headers[HttpHeaders.LOCATION] = f"{url}"

    return ds_response


@router.get("/{dataset_id}")
def get_dataset(service: DatasetServiceDep, dataset_id: UUID) -> DatasetResponse:
    dataset = service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{dataset_id}' not found.",
        )

    return dataset


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(service: DatasetServiceDep, dataset_id: UUID) -> None:
    try:
        service.delete_dataset(dataset_id)
    except Exception as e:
        logger.error(f"Unexpected error deleting dataset ID from DB and S3: {dataset_id}. {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error deleting dataset for ID: {dataset_id}",
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
