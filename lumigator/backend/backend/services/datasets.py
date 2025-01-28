import csv
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import BinaryIO
from uuid import UUID

from datasets import load_dataset
from fastapi import UploadFile
from loguru import logger
from lumigator_schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse
from lumigator_schemas.extras import ListingResponse
from mypy_boto3_s3.client import S3Client
from pydantic import ByteSize
from s3fs import S3FileSystem

from backend.records.datasets import DatasetRecord
from backend.repositories.datasets import DatasetRepository
from backend.services.exceptions.dataset_exceptions import (
    DatasetInvalidError,
    DatasetMissingFieldsError,
    DatasetNotFoundError,
    DatasetSizeError,
    DatasetUpstreamError,
)
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

    :param input: the input buffer
    :param output: the output buffer (which is updated to contain the parsed dataset)
    :param max_size: the maximum allowed size of the output buffer
    :raises DatasetSizeError: if the size of the output buffer (file) is too large
    """
    actual_size = 0
    for chunk in input:
        actual_size += output.write(chunk)
        if actual_size > max_size:
            raise DatasetSizeError(max_size.human_readable(decimal=True)) from None
    return actual_size


def validate_dataset_format(filename: str, format: DatasetFormat):
    """Validates the dataset identified by the filename, based on the format.

    :param filename: the filename of the dataset to validate
    :param format: the dataset format (e.g. 'job')
    :raises DatasetInvalidError: if there is a problem with the dataset file format
    :raises DatasetMissingFieldsError: if the dataset is missing any required fields
    """
    try:
        match format:
            case DatasetFormat.JOB:
                validate_experiment_dataset(filename)
            case _:
                # Should not be reachable
                raise ValueError(f"Unknown dataset format: {format}")
    except UnicodeError as e:
        logger.opt(exception=e).info("Error processing dataset upload.")
        raise DatasetInvalidError("not a CSV file") from e


def validate_experiment_dataset(filename: str):
    """Validates the dataset (CSV) file to ensure all required fields are present.

    :param filename: the filename of the dataset to validate
    :raises DatasetMissingFieldsError: if the dataset is missing any of the required fields
    """
    with Path(filename).open() as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])

        missing_fields = REQUIRED_EXPERIMENT_FIELDS.difference(fields)
        if missing_fields:
            raise DatasetMissingFieldsError(missing_fields) from None


def dataset_has_gt(filename: str) -> bool:
    """Returns true if the dataset located at the supplied path (filename) has a ground truth
    column with all of its rows correctly populated, otherwise false.
    """
    dataset = load_dataset("csv", data_files=filename, split="train")

    if GT_FIELD not in dataset.column_names:
        return False

    # True only if every value in dataset[GT_FIELD] is not None or empty.
    return all(value is not None and value.strip() != "" for value in dataset[GT_FIELD])


class DatasetService:
    def __init__(
        self, dataset_repo: DatasetRepository, s3_client: S3Client, s3_filesystem: S3FileSystem
    ):
        self.dataset_repo = dataset_repo
        self.s3_client = s3_client
        self.s3_filesystem = s3_filesystem

    def _get_dataset_record(self, dataset_id: UUID) -> DatasetRecord | None:
        return self.dataset_repo.get(dataset_id)

    def _get_dataset_record_by_job_id(self, job_id: UUID) -> DatasetRecord | None:
        return self.dataset_repo.get_by_job_id(job_id)

    def _get_s3_path(self, dataset_key: str) -> str:
        return f"s3://{Path(settings.S3_BUCKET) / dataset_key}"

    def _get_s3_key(self, dataset_id: UUID, filename: str) -> str:
        """Generate the S3 key for the dataset contents.

        The original filename is included in the key so the filename stays the same
        when downloading the object from S3.
        """
        return f"{settings.S3_DATASETS_PREFIX}/{dataset_id}/{filename}"

    def _save_dataset_to_s3(self, temp_fname, record):
        """Converts the specified file to a set of HuggingFace dataset formatted files,
        along with a newly recreated CSV file. The files are stored in an S3 bucket.

        :param temp_fname: temporary file name to read the dataset from
        :param record: the dataset record (DatasetRecord)
        :raises DatasetUpstreamError: if there is an exception interacting with S3
        """
        # Temp file to be used to contain the recreated CSV file.
        temp = NamedTemporaryFile(delete=False)

        try:
            # Load the CSV file as HF dataset
            dataset_hf = load_dataset("csv", data_files=temp_fname, split="train")

            # Upload to S3
            dataset_key = self._get_s3_key(record.id, record.filename)
            dataset_path = self._get_s3_path(dataset_key)
            # Deprecated!!!
            dataset_hf.save_to_disk(dataset_path, fs=self.s3_filesystem)

            # Use the converted HF format files to rebuild the CSV and store it as 'dataset.csv'.
            dataset_hf.to_csv(temp.name, index=False)
            self.s3_filesystem.put_file(temp.name, f"{dataset_path}/dataset.csv")
        except Exception as e:
            # if a record was already created, delete it from the DB
            if record:
                self.dataset_repo.delete(record.id)

            raise DatasetUpstreamError("s3", "error attempting to save dataset to S3", e) from e
        finally:
            # Clean up temp file
            Path(temp.name).unlink()

    def upload_dataset(
        self,
        dataset: UploadFile,
        format: DatasetFormat,
        run_id: UUID | None = None,
        generated: bool = False,
        generated_by: str | None = None,
    ) -> DatasetResponse:
        """Attempts to upload and convert the specified dataset (CSV) to HF format which is then
        stored in S3.

        :return: Information on the uploaded dataset
        :rtype: DatasetResponse
        :raises DatasetSizeError: if the dataset is too large
        :raises DatasetInvalidError: if the dataset is invalid
        :raises DatasetMissingFieldsError: if the dataset is missing any of the required fields
        :raises DatasetUpstreamError: if there is an exception interacting with S3
        """
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
                filename=dataset.filename,
                format=format,
                size=actual_size,
                ground_truth=has_gt,
                run_id=run_id,
                generated=generated,
                generated_by=generated_by,
            )

            # convert the dataset to HF format and save it to S3
            self._save_dataset_to_s3(temp.name, record)
        finally:
            # Cleanup temp file
            Path(temp.name).unlink()

        return DatasetResponse.model_validate(record)

    def get_dataset(self, dataset_id: UUID) -> DatasetResponse | None:
        """Gets the dataset record by its ID.

        :param dataset_id: dataset ID
        :return: Information on the dataset
        :rtype: DatasetResponse
        :raises DatasetNotFoundError: if there is no dataset record with that ID
        """
        record = self._get_dataset_record(dataset_id)
        if record is None:
            raise DatasetNotFoundError(dataset_id) from None

        return DatasetResponse.model_validate(record)

    def get_dataset_by_job_id(self, job_id: UUID) -> DatasetResponse | None:
        record = self._get_dataset_record_by_job_id(job_id)
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

        :param dataset_id: dataset ID to delete
        :raises DatasetNotFoundError: if there is no dataset record with that ID
        :raises DatasetUpstreamError: if there is an exception deleting the dataset from S3
        """
        record = self._get_dataset_record(dataset_id)
        # Early return if the record does not exist (for idempotency).
        if record is None:
            raise DatasetNotFoundError(dataset_id) from None

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
        except Exception as e:
            raise DatasetUpstreamError(
                "s3", f"error attempting to delete dataset {dataset_id} from S3", e
            ) from e

        # Getting this far means we are OK to remove the record from the DB.
        self.dataset_repo.delete(record.id)

    def get_dataset_download(
        self, dataset_id: UUID, extension: str | None = None
    ) -> DatasetDownloadResponse:
        """Generate pre-signed download URLs for dataset files.

        When supplied, only URLs for files that match the specified extension are returned.

        :param dataset_id: ID of the dataset to generate pre-signed download URLs for
        :param extension: File extension used to determine which files to generate URLs for
        :return: Pre-signed download URLs
        :rtype: DatasetDownloadResponse
        :raises DatasetNotFoundError: if the dataset cannot be found in S3
        :raises DatasetUpstreamError: if there is an exception interacting with S3
        """
        # Sanitize the input for a file extension.
        extension = extension.strip().lower() if extension and extension.strip() else None

        record = self._get_dataset_record(dataset_id)
        if record is None:
            raise DatasetNotFoundError(dataset_id, "error getting dataset download") from None

        dataset_key = self._get_s3_key(dataset_id, record.filename)

        try:
            # Call list_objects_v2 to get all objects whose key names start with `dataset_key`
            s3_response = self.s3_client.list_objects_v2(
                Bucket=settings.S3_BUCKET, Prefix=dataset_key
            )

            if s3_response.get("KeyCount") == 0:
                raise DatasetNotFoundError(
                    dataset_id, f"No S3 files found with prefix '{dataset_key}'"
                ) from None

            download_urls = []
            for s3_object in s3_response["Contents"]:
                # Ignore files that don't end with the extension if it was specified
                if extension and not s3_object["Key"].lower().endswith(extension):
                    continue

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
            msg = f"Error generating pre-signed download URLs for dataset {dataset_id}"
            raise DatasetUpstreamError("s3", msg, e) from e

        return DatasetDownloadResponse(id=dataset_id, download_urls=download_urls)

    def list_datasets(self, skip: int = 0, limit: int = 100) -> ListingResponse[DatasetResponse]:
        total = self.dataset_repo.count()
        records = self.dataset_repo.list(skip, limit)
        return ListingResponse(
            total=total,
            items=[DatasetResponse.model_validate(x) for x in records],
        )
