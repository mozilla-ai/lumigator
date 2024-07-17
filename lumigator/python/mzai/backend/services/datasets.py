import csv
import os
import warnings
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import BinaryIO
from uuid import UUID

import s3fs
from datasets import load_dataset
from fastapi import HTTPException, UploadFile, status
from loguru import logger
from mypy_boto3_s3.client import S3Client
from pydantic import ByteSize

from mzai.backend.records.datasets import DatasetRecord
from mzai.backend.repositories.datasets import DatasetRepository
from mzai.backend.settings import settings
from mzai.schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse
from mzai.schemas.extras import ListingResponse

ALLOWED_EXPERIMENT_FIELDS: set[str] = {"examples", "ground_truth"}
REQUIRED_EXPERIMENT_FIELDS: set[str] = {"examples"}


def validate_file_size(input: BinaryIO, output: BinaryIO, max_size: ByteSize) -> int:
    """Write the input contents to an output buffer while validating its size.

    A file is not completely sent to the server before the app starts processing the request.
    We could mandate a `Content-Length` header within a given range, but there is nothing
    stopping an "attacker" from sending a file with a faked out header value.
    Our best bet is to traverse the file in chunks and throw an error if its too large.
    We can then process the file as a whole once its been written to a buffer on the server.

    Reference: https://github.com/tiangolo/fastapi/issues/362#issuecomment-584104025
    """
    actual_size = 0
    for chunk in input:
        actual_size += output.write(chunk)
        if actual_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File upload exceeds the {max_size.human_readable(decimal=True)} limit.",
            )
    return actual_size


def validate_dataset_format(filename: str, format: DatasetFormat):
    try:
        match format:
            case DatasetFormat.EXPERIMENT:
                validate_experiment_dataset(filename)
            case _:
                # Should not be reachable
                raise ValueError(f"Unknown dataset format: {format}")
    except UnicodeError as e:
        logger.opt(exception=e).info("Error processing dataset upload.")
        http_exception = HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Dataset is not a valid CSV file.",
        )
        raise http_exception from e


def validate_experiment_dataset(filename: str):
    with Path(filename).open() as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])

        missing_fields = REQUIRED_EXPERIMENT_FIELDS.difference(fields)
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Experiment dataset is missing the required fields: {missing_fields}.",
            )

        extra_fields = fields.difference(ALLOWED_EXPERIMENT_FIELDS)
        if extra_fields:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Experiment dataset contains the invalid fields: {extra_fields}. "
                    f"Only {ALLOWED_EXPERIMENT_FIELDS} are allowed."
                ),
            )


class DatasetService:
    def __init__(self, dataset_repo: DatasetRepository, s3_client: S3Client):
        self.dataset_repo = dataset_repo
        self.s3_client = s3_client
        self.s3_filesystem = s3fs.S3FileSystem()

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
            # We are writing to a tempfile because we have to re-process it multiple times
            # Using an in-memory buffer would be prone to losing the contents when closed
            with temp as buffer:
                actual_size = validate_file_size(dataset.file, buffer, settings.MAX_DATASET_SIZE)

            # Validate format
            validate_dataset_format(temp.name, format)

            # Create DB record
            record = self.dataset_repo.create(
                filename=dataset.filename,
                format=format,
                size=actual_size,
            )

            # Load the CSV file as HF dataset
            dataset_hf = load_dataset("csv", data_files=temp.name, split="train")

            # Upload to S3
            warnings.warn(f"FSSPEC_S3_KEY: {os.environ['LOCAL_FSSPEC_S3_KEY']}", stacklevel=2)
            warnings.warn(f"FSSPEC_S3_SECRET: {os.environ['LOCAL_FSSPEC_S3_SECRET']}", stacklevel=2)
            warnings.warn(
                f"FSSPEC_S3_ENDPOINT_URL: {os.environ['LOCAL_FSSPEC_S3_ENDPOINT_URL']}",
                stacklevel=2,
            )

            dataset_key = self._get_s3_key(record.id, record.filename)

            dataset_path = f"s3://{ Path(settings.S3_BUCKET) / dataset_key }"
            dataset_hf.save_to_disk(dataset_path, fs=self.s3_filesystem)

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
