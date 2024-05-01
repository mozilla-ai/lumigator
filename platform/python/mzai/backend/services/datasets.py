from uuid import UUID

from fastapi import HTTPException, UploadFile, status

from mzai.backend.repositories.datasets import DatasetRepository
from mzai.backend.settings import settings
from mzai.schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse
from mzai.schemas.extras import ListingResponse


class DatasetService:
    def __init__(self, dataset_repo: DatasetRepository, s3_client):
        self.dataset_repo = dataset_repo
        self.s3_client = s3_client

    # TODO: Abstract this so all services have the same exception logic
    def _raise_not_found(self, dataset_id: UUID):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Dataset {dataset_id} not found.")

    def _dataset_object_key(self, dataset_id: UUID) -> str:
        return f"{settings.S3_DATASETS_PREFIX}/{dataset_id}"

    def upload_dataset(self, dataset: UploadFile, format: DatasetFormat) -> DatasetResponse:
        # Create DB record
        record = self.dataset_repo.create(
            filename=dataset.filename,
            format=format,
            size=0,
        )

        # Upload to S3
        dataset_key = self._dataset_object_key(record.id)
        self.s3_client.upload_fileobj(dataset.file, settings.S3_BUCKET, dataset_key)

        # Response
        return DatasetResponse.model_validate(record)

    def get_dataset(self, dataset_id: UUID) -> DatasetResponse:
        record = self.dataset_repo.get(dataset_id)
        if not record:
            self._raise_not_found(dataset_id)
        return DatasetResponse.model_validate(record)

    def get_dataset_download(self, dataset_id: UUID) -> DatasetDownloadResponse:
        if not self.dataset_repo.exists(id=dataset_id):
            self._raise_not_found(dataset_id)

        dataset_key = self._dataset_object_key(dataset_id)
        download_url = self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET, "Key": dataset_key},
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
