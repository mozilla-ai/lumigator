import csv
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import BinaryIO
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from loguru import logger
from pydantic import ByteSize

from mzai.backend.records.datasets import DatasetRecord
from mzai.backend.repositories.datasets import DatasetRepository
from mzai.backend.settings import settings
from mzai.backend.types import S3Client
from mzai.schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse
from mzai.schemas.extras import ListingResponse

UnprocessableEntityError = UnicodeDecodeError
"""An error we expect because someone uploaded an invalid file format."""


def write_temporary_dataset(input: BinaryIO, buffer: BinaryIO, max_size: ByteSize) -> bytes:
    dataset_size = 0
    for chunk in input:
        dataset_size += len(chunk)
        if dataset_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Dataset exceeds the {max_size.human_readable(decimal=True)} limit.",
            )
        buffer.write(chunk)
    return dataset_size


def validate_dataset_format(filename: str, format: DatasetFormat):
    try:
        match format:
            case DatasetFormat.EXPERIMENT:
                validate_experiment_dataset(filename)
    except UnprocessableEntityError as e:
        logger.opt(exception=e).info("Error processing dataset upload.")
        http_exception = HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Dataset is not a valid CSV file.",
        )
        raise http_exception from e


def validate_experiment_dataset(filename: str):
    with Path(filename).open() as f:
        reader = csv.DictReader(f)
        fields: list[str] = reader.fieldnames or []
        if "examples" not in fields:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Experiment dataset must contain an 'examples' field.",
            )
        allowed_fields = {"examples", "ground_truth"}
        invalid_fields = {x for x in fields if x not in allowed_fields}
        if invalid_fields:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Experiment dataset contains invalid fields {invalid_fields}. "
                    f"Only {allowed_fields} are allowed."
                ),
            )


class DatasetService:
    def __init__(self, dataset_repo: DatasetRepository, s3_client: S3Client):
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
        temp = NamedTemporaryFile(delete=False)
        try:
            # Write to tempfile and validate size
            with temp as buffer:
                real_size = write_temporary_dataset(dataset.file, buffer, settings.MAX_DATASET_SIZE)

            # Validate format
            validate_dataset_format(temp.name, format)

            # Create DB record
            record = self.dataset_repo.create(
                filename=dataset.filename,
                format=format,
                size=real_size,
            )

            # Upload to S3
            dataset_key = self._get_s3_key(record.id, record.filename)
            self.s3_client.upload_file(temp.name, settings.S3_BUCKET, dataset_key)

        finally:
            # Cleanup temp file
            Path(temp.name).unlink()

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
