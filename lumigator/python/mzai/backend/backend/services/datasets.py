import csv
import traceback
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import BinaryIO
from uuid import UUID

from datasets import load_dataset
from fastapi import HTTPException, UploadFile, status
from loguru import logger
from lumigator_schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse
from lumigator_schemas.extras import ListingResponse
from mypy_boto3_s3.client import S3Client
from pydantic import ByteSize
from s3fs import S3FileSystem

from backend.records.datasets import DatasetRecord
from backend.repositories.datasets import DatasetRepository
from backend.settings import settings

GT_FIELD: str = "ground_truth"
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
            case DatasetFormat.JOB:
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


def dataset_has_gt(filename: str) -> bool:
    with Path(filename).open() as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        has_gt = GT_FIELD in fields

    return has_gt


class DatasetService:
    def __init__(
        self, dataset_repo: DatasetRepository, s3_client: S3Client, s3_filesystem: S3FileSystem
    ):
        self.dataset_repo = dataset_repo
        self.s3_client = s3_client
        self.s3_filesystem = s3_filesystem

    def _raise_not_found(self, dataset_id: UUID) -> None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Dataset '{dataset_id}' not found.")

    def _raise_unhandled_exception(self, e: Exception) -> None:
        traceback.print_exception(type(e), e, e.__traceback__)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e)) from e

    def _get_dataset_record(self, dataset_id: UUID) -> DatasetRecord | None:
        return self.dataset_repo.get(dataset_id)

    def _get_s3_path(self, dataset_key: str) -> str:
        return f"s3://{ Path(settings.S3_BUCKET) / dataset_key }"

    def _get_s3_key(self, dataset_id: UUID, filename: str) -> str:
        """Generate the S3 key for the dataset contents.

        The original filename is included in the key so the filename stays the same
        when downloading the object from S3.
        """
        return f"{settings.S3_DATASETS_PREFIX}/{dataset_id}/{filename}"

    def _save_dataset_to_s3(self, temp_fname, record):
        """Loads a dataset, converts it to HF dataset format, and saves it on S3."""
        try:
            # Load the CSV file as HF dataset
            dataset_hf = load_dataset("csv", data_files=temp_fname, split="train")

            # Upload to S3
            dataset_key = self._get_s3_key(record.id, record.filename)
            dataset_path = self._get_s3_path(dataset_key)
            # Deprecated!!!
            dataset_hf.save_to_disk(dataset_path, fs=self.s3_filesystem)
        except Exception as e:
            # if a record was already created, delete it from the DB
            if record:
                self.dataset_repo.delete(record.id)

            self._raise_unhandled_exception(e)

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

            # Verify whether the dataset contains ground truth
            has_gt = dataset_has_gt(temp.name)

            # Create DB record
            record = self.dataset_repo.create(
                filename=dataset.filename, format=format, size=actual_size, ground_truth=has_gt
            )

            # convert the dataset to HF format and save it to S3
            self._save_dataset_to_s3(temp.name, record)

        finally:
            # Cleanup temp file
            Path(temp.name).unlink()

        return DatasetResponse.model_validate(record)

    def get_dataset(self, dataset_id: UUID) -> DatasetResponse | None:
        record = self._get_dataset_record(dataset_id)
        if record is None:
            return None

        return DatasetResponse.model_validate(record)

    def get_dataset_s3_path(self, dataset_id: UUID) -> str | None:
        record = self._get_dataset_record(dataset_id)
        if record is None:
            return None

        dataset_key = self._get_s3_key(record.id, record.filename)
        dataset_path = self._get_s3_path(dataset_key)
        return dataset_path

    def delete_dataset(self, dataset_id: UUID) -> None:
        """When the dataset exists, attempts to delete it from both an S3 bucket and the DB.

        Raises exceptions it encounters dealing with S3, except when the file is not found in S3
        (in this case it deletes the orphaned record from the DB).

        This operation is idempotent, calling it with a record that never existed, or that has
        already been deleted, will not raise an error.
        """
        record = self._get_dataset_record(dataset_id)
        # Early return if the record does not exist (for idempotency).
        if record is None:
            return None

        try:
            # S3 delete is called first, if this fails for any other reason that the file not being
            # found, then the DB delete won't take place, and an exception raised.
            dataset_key = self._get_s3_key(record.id, record.filename)
            dataset_path = self._get_s3_path(dataset_key)
            self.s3_filesystem.rm(dataset_path, recursive=True)
        except FileNotFoundError as e:
            # File not found errors are allowed, but we perform clean-up in this situation.
            logger.warning(
                f"Dataset ID: {dataset_id} was present in the DB but not found on S3... "
                f"Cleaning up DB by removing ID. {e}"
            )

        # Getting this far means we are OK to remove the record from the DB.
        self.dataset_repo.delete(record.id)

    def get_dataset_download(self, dataset_id: UUID) -> DatasetDownloadResponse:
        """Generate presigned download URLs for dataset files."""
        record = self._get_dataset_record(dataset_id)
        dataset_key = self._get_s3_key(dataset_id, record.filename)

        try:
            # Call list_objects_v2 to get all objects whose key names start with `dataset_key`
            s3_response = self.s3_client.list_objects_v2(
                Bucket=settings.S3_BUCKET, Prefix=dataset_key
            )

            if s3_response.get("KeyCount") == 0:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, f"No files found with prefix '{dataset_key}'."
                )

            download_urls = []
            for s3_object in s3_response["Contents"]:
                download_url = self.s3_client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": settings.S3_BUCKET,
                        "Key": s3_object["Key"],
                    },
                    ExpiresIn=settings.S3_URL_EXPIRATION,
                )
                download_urls.append(download_url)

        except Exception as e:
            self._raise_unhandled_exception(e)

        return DatasetDownloadResponse(id=dataset_id, download_urls=download_urls)

    def list_datasets(self, skip: int = 0, limit: int = 100) -> ListingResponse[DatasetResponse]:
        total = self.dataset_repo.count()
        records = self.dataset_repo.list(skip, limit)
        return ListingResponse(
            total=total,
            items=[DatasetResponse.model_validate(x) for x in records],
        )
