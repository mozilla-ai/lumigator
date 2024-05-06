from uuid import UUID

from fastapi import HTTPException, UploadFile, status

from mzai.backend.records.datasets import DatasetRecord
from mzai.backend.repositories.datasets import DatasetRepository
from mzai.backend.settings import settings
from mzai.schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse
from mzai.schemas.extras import ListingResponse


class DatasetService:
    def __init__(self, dataset_repo: DatasetRepository, s3_client):
        self.dataset_repo = dataset_repo
        self.s3_client = s3_client

    def _raise_not_found(self, dataset_id: UUID) -> None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Dataset '{dataset_id}' not found.")

    def _get_dataset_record(self, dataset_id: UUID) -> DatasetRecord:
        record = self.dataset_repo.get(dataset_id)
        if record is None:
            self._raise_not_found(dataset_id)
        return record

    def _get_s3_key(self, dataset_id: UUID, filename: str) -> str:
        """Generate the S3 key for the dataset contents.

        The original filename is included in the key so the filename stays the same
        when downloading the object from S3.
        """
        return f"{settings.S3_DATASETS_PREFIX}/{dataset_id}/{filename}"

    def upload_dataset(self, dataset: UploadFile, format: DatasetFormat) -> DatasetResponse:
        # TODO (MZPLATFORM-79): Add validation logic to dataset uploads

        # Create DB record
        record = self.dataset_repo.create(
            filename=dataset.filename,
            format=format,
            size=dataset.size,
        )

        # Upload to S3
        dataset_key = self._get_s3_key(record.id, record.filename)
        self.s3_client.upload_fileobj(dataset.file, settings.S3_BUCKET, dataset_key)

        # Response
        return DatasetResponse.model_validate(record)

    def get_dataset(self, dataset_id: UUID) -> DatasetResponse:
        record = self._get_dataset_record(dataset_id)
        return DatasetResponse.model_validate(record)

    def delete_dataset(self, dataset_id: UUID) -> None:
        record = self._get_dataset_record(dataset_id)

        # Delete from S3
        # S3 delete is called first, since if this fails the DB delete won't take place
        dataset_key = self._get_s3_key(record.id, record.filename)
        self.s3_client.delete_object(Bucket=settings.S3_BUCKET, Key=dataset_key)

        # Delete DB record
        self.dataset_repo.delete(record.id)

    def get_dataset_download(self, dataset_id: UUID) -> DatasetDownloadResponse:
        record = self._get_dataset_record(dataset_id)

        # Generate presigned download URL for the object
        dataset_key = self._get_s3_key(dataset_id, record.filename)
        download_url = self.s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": dataset_key,
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
