from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Form, Query, UploadFile, status
from lumigator_schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse
from lumigator_schemas.extras import ListingResponse
from starlette.requests import Request
from starlette.responses import Response

from backend.api.deps import DatasetServiceDep
from backend.api.http_headers import HttpHeaders
from backend.services.exceptions.base_exceptions import ServiceError
from backend.services.exceptions.dataset_exceptions import (
    DatasetInvalidError,
    DatasetMissingFieldsError,
    DatasetNotAvailableError,
    DatasetNotFoundError,
    DatasetSizeError,
    DatasetUpstreamError,
)
from backend.settings import settings

router = APIRouter()


def dataset_exception_mappings() -> dict[type[ServiceError], HTTPStatus]:
    return {
        DatasetNotFoundError: status.HTTP_404_NOT_FOUND,
        DatasetMissingFieldsError: status.HTTP_403_FORBIDDEN,
        DatasetUpstreamError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        DatasetSizeError: status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        DatasetInvalidError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        DatasetNotAvailableError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    }


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Dataset successfully uploaded"},
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {
            "description": f"Max dataset size ({settings.MAX_DATASET_SIZE_HUMAN_READABLE})"
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Invalid CSV file"},
    },
)
def upload_dataset(
    service: DatasetServiceDep,
    dataset: UploadFile,
    format: Annotated[DatasetFormat, Form()],
    request: Request,
    response: Response,
    run_id: Annotated[
        UUID | None, Form(description="Provide the Job ID that generated this dataset.")
    ] = None,
    generated: Annotated[bool, Form(description="Is the dataset AI-generated?")] = False,
    generated_by: Annotated[
        str | None, Form(description="The name of the AI model that generated this dataset.")
    ] = None,
) -> DatasetResponse:
    """Uploads the dataset for use in Lumigator.

    An uploaded dataset is parsed into HuggingFace format files and stored alongside a
    recreated version of the input dataset.

    NOTE: The recreated version of the CSV file may not have identical delimiters as it will follow
    the format that HuggingFace uses when it generates the CSV.
    """
    ds_response = service.upload_dataset(
        dataset, format, run_id=run_id, generated=generated, generated_by=generated_by
    )

    url = request.url_for(get_dataset.__name__, dataset_id=ds_response.id)
    response.headers[HttpHeaders.LOCATION] = f"{url}"

    return ds_response


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
def get_dataset_download(
    service: DatasetServiceDep,
    dataset_id: UUID,
    extension: str | None = Query(
        default=None,
        description="When specified, will be used to return only URLs for files which have "
        "a matching file extension. Wildcards are not accepted. "
        "By default all files are returned. e.g. csv",
    ),
) -> DatasetDownloadResponse:
    """Returns a collection of pre-signed URLs which can be used to download the dataset."""
    return service.get_dataset_download(dataset_id, extension)
