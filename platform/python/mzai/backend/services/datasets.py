from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from loguru import logger

from mzai.backend.records.datasets import DatasetRecord
from mzai.backend.repositories.datasets import DatasetRepository
from mzai.backend.settings import settings
from mzai.schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse
from mzai.schemas.extras import ListingResponse

ALLOWED_CONTENT_TYPES = {"text/csv"}


class DatasetService:
    def __init__(
        self,
        dataset_repo: DatasetRepository,
        s3_client,
        max_dataset_size: int | None = None,
    ):
        self.dataset_repo = dataset_repo
        self.s3_client = s3_client
        self.max_dataset_size = max_dataset_size

    # TODO: Abstract this so all services have the same exception logic
    def _get_dataset_record(self, dataset_id: UUID) -> DatasetRecord:
        record = self.dataset_repo.get(dataset_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Dataset {dataset_id} not found.")
        return record

    def _dataset_s3_key(self, dataset_id: UUID) -> str:
        return f"{settings.S3_DATASETS_PREFIX}/{dataset_id}"

    def _validate_upload_file(self, dataset: UploadFile, format: DatasetFormat) -> None:
        # Validation for all datasets
        if dataset.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                f"Dataset content type must be one of the following: {ALLOWED_CONTENT_TYPES}",
            )
        # Validation per dataset format
        match format:
            case DatasetFormat.EXPERIMENT:
                self._validate_experiment_format(dataset)
            case _:
                # This should never be reached
                logger.error(f"Encountered unknown dataset format: '{format}'")
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _validate_experiment_format(self, dataset: UploadFile) -> None:
        pass

    def upload_dataset(self, dataset: UploadFile, format: DatasetFormat) -> DatasetResponse:
        # Create DB record
        record = self.dataset_repo.create(
            filename=dataset.filename,
            format=format,
            size=dataset.size,
        )

        # Upload to S3
        dataset_key = self._dataset_s3_key(record.id)
        self.s3_client.upload_fileobj(dataset.file, settings.S3_BUCKET, dataset_key)

        # Response
        return DatasetResponse.model_validate(record)

    def get_dataset(self, dataset_id: UUID) -> DatasetResponse:
        record = self._get_dataset_record(dataset_id)
        return DatasetResponse.model_validate(record)

    def get_dataset_download(self, dataset_id: UUID) -> DatasetDownloadResponse:
        record = self._get_dataset_record(dataset_id)

        # Generate presigned download URL for the object
        dataset_key = self._dataset_s3_key(dataset_id)
        download_url = self.s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": dataset_key,
                # Sets a header to download the object with the original filename
                "ResponseContentDisposition": f"attachment; filename = {record.filename}",
            },
            ExpiresIn=settings.S3_URL_EXPIRATION,
        )

        return DatasetDownloadResponse(id=dataset_id, download_url=download_url)

    def list_datasets(self, skip: int = 0, limit: int = 100) -> ListingResponse[DatasetResponse]:
        total = self.dataset_repo.count()
        records = self.dataset_repo.list(skip, limit)
        return ListingResponse(
            total=total,
            items=[DatasetResponse.model_validate(x) for x in records],
        )
