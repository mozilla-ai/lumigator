import asyncio
import csv
import json
import re
from http import HTTPStatus
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any
from urllib.parse import urljoin
from uuid import UUID

# ADD YOUR JOB IMPORT HERE #
# Only the definition package
############################
import evaluator.definition
import inference.definition

############################
import loguru
import requests
from fastapi import BackgroundTasks, UploadFile
from lumigator_schemas.datasets import DatasetFormat
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    JobConfig,
    JobCreate,
    JobEvalConfig,
    JobInferenceConfig,
    JobLogsResponse,
    JobResponse,
    JobResultDownloadResponse,
    JobResultObject,
    JobResultResponse,
    JobStatus,
    JobType,
)
from ray.job_submission import JobSubmissionClient
from s3fs import S3FileSystem
from sqlalchemy.sql.expression import or_
from starlette.datastructures import Headers

from backend.ray_submit.submission import RayJobEntrypoint, submit_ray_job
from backend.records.jobs import JobRecord
from backend.repositories.jobs import JobRepository, JobResultRepository
from backend.services.datasets import DatasetService
from backend.services.exceptions.dataset_exceptions import DatasetMissingFieldsError
from backend.services.exceptions.job_exceptions import (
    JobNotFoundError,
    JobTypeUnsupportedError,
    JobUpstreamError,
    JobValidationError,
)
from backend.services.exceptions.secret_exceptions import SecretDecryptionError, SecretNotFoundError
from backend.services.secrets import SecretService
from backend.settings import settings

# ADD YOUR JOB IMPORT HERE #
############################
job_modules = [
    {"name": "evaluator", "definition": evaluator.definition},
    {"name": "inference", "definition": inference.definition},
    {"name": "annotation", "definition": inference.definition},
]
############################
job_settings_map = {
    getattr(job_module["definition"], f"{job_module['name'].upper()}_JOB_DEFINITION").type: getattr(
        job_module["definition"], f"{job_module['name'].upper()}_JOB_DEFINITION"
    )
    for job_module in job_modules
}

DEFAULT_SKIP = 0
DEFAULT_LIMIT = 100
DEFAULT_POST_INFER_JOB_TIMEOUT_SEC = 10 * 60
JobSpecificRestrictedConfig = type[JobEvalConfig | JobInferenceConfig]


# The end result should be that InferenceJobConfig is actually JobInferenceConfig
# (resp. Eval)
# For the moment, something will convert one into the other, and we'll decide where
# to put this. The jobs should ideally have no dependency towards the backend.


class JobService:
    """Job service is responsible for managing jobs in Lumigator."""

    NON_TERMINAL_STATUS = [
        JobStatus.CREATED.value,
        JobStatus.PENDING.value,
        JobStatus.RUNNING.value,
    ]
    """list: A list of non-terminal job statuses."""

    # TODO: rely on https://github.com/ray-project/ray/blob/7c2a200ef84f17418666dad43017a82f782596a3/python/ray/dashboard/modules/job/common.py#L53
    TERMINAL_STATUS = [JobStatus.FAILED.value, JobStatus.SUCCEEDED.value, JobStatus.STOPPED.value]
    """list: A list of terminal job statuses."""

    SAFE_JOB_NAME_REGEX = re.compile(r"[^\w\-_.]")
    """A regex pattern to match unsafe characters in job names."""

    JOB_NAME_REPLACEMENT_CHAR = "-"
    """The character to replace unsafe characters in job names."""

    def __init__(
        self,
        job_repo: JobRepository,
        result_repo: JobResultRepository,
        ray_client: JobSubmissionClient,
        dataset_service: DatasetService,
        secret_service: SecretService,
        background_tasks: BackgroundTasks,
    ):
        self._job_repo = job_repo
        self._result_repo = result_repo
        self._ray_client = ray_client
        self._dataset_service = dataset_service
        self._secret_service = secret_service
        self._background_tasks = background_tasks

    def _get_job_record_per_type(self, job_type: str) -> list[JobRecord]:
        records = self._job_repo.get_by_job_type(job_type)
        if records is None:
            return []
        return records

    def _get_job_record(self, job_id: UUID) -> JobRecord:
        """Gets a job from the repository (database) by ID.

        :param job_id: the ID of the job to retrieve
        :return: the job record which includes information on whether a job belongs to an experiment
        :rtype: JobRecord
        :raises JobNotFoundError: If the job does not exist
        """
        record = self._job_repo.get(job_id)
        if record is None:
            raise JobNotFoundError(job_id) from None

        return record

    async def stop_job(self, job_id: UUID) -> bool:
        """Attempts to stop an existing job in Ray by ID, and waits (for up to 10 seconds) for it to 'complete'.

        :param job_id: The ID of the job to stop
        :returns: True if the job was successfully stopped, False otherwise
        """
        try:
            self._stop_job(job_id)
        except JobNotFoundError:
            # If the job is not found, we consider it stopped
            return True

        try:
            status = await self.wait_for_job_complete(job_id, max_wait_time_sec=10)
        except JobUpstreamError as e:
            loguru.logger.error("Failed to stop job {}: {}", job_id, e)
            return False

        return status and status.lower() == JobStatus.STOPPED.value

    def _stop_job(self, job_id: UUID):
        """Stops an existing job in Ray by ID.

        :param job_id: The ID of the job to stop
        :raises JobNotFoundError: If the job doesn't exist in Ray
        :raises JobUpstreamError: If there is an unexpected error with the upstream service while stopping the job
        """
        resp = requests.post(urljoin(settings.RAY_JOBS_URL, f"{job_id}/stop"), timeout=5)  # 5 seconds
        if resp.status_code == HTTPStatus.NOT_FOUND:
            raise JobNotFoundError(job_id, "Unable to stop Ray job") from None
        elif resp.status_code != HTTPStatus.OK:
            raise JobUpstreamError(
                "ray",
                f"Unexpected status code when trying to stop job: {resp.status_code}, error: {resp.text or ''}",
            ) from None

    def _update_job_record(self, job_id: UUID, **updates) -> JobRecord:
        """Updates an existing job record in the repository (database) by ID.

        :param job_id: The ID of the job to update
        :param updates: The updates to update the job record
        :return: The updated job record
        :rtype: JobRecord
        :raises JobNotFoundError: If the job does not exist in the database
        """
        record = self._job_repo.update(job_id, **updates)
        if record is None:
            raise JobNotFoundError(job_id) from None

        return record

    def _get_results_s3_key(self, job_id: UUID) -> str:
        """Given a job ID, returns the S3 key identifying where job results should be stored.

        The S3 key is constructed from:
        - settings.S3_JOB_RESULTS_PREFIX: the path where jobs are stored
        - settings.S3_JOB_RESULTS_FILENAME: a filename template that is to be formatted with some of
                the job record's metadata (e.g. name/id)

        NOTE: The job's name is sanitized to be S3-safe.

        :param job_id: The ID of the job to retrieve the S3 key for
        :return: The returned string contains the S3 key *excluding the bucket and s3 prefix*.
        :raises JobNotFoundError: If the job does not exist.
        """
        record = self._get_job_record(job_id)
        if record.name is None:
            raise JobValidationError(f"Job {job_id} is missing 'name'") from None

        return str(
            Path(settings.S3_JOB_RESULTS_PREFIX)
            / settings.S3_JOB_RESULTS_FILENAME.format(
                job_name=self.sanitize_job_name(str(record.name)), job_id=record.id
            )
        )

    def _get_s3_uri(self, job_id: UUID) -> str:
        """Construct a full S3 URI for job result artifacts.

        :param job_id: The ID of the job to retrieve the S3 URI for.
        :return: The S3 URI for the job results.
        :raises JobNotFoundError: If the job does not exist.
        """
        return f"s3://{settings.S3_BUCKET}/{self._get_results_s3_key(job_id)}"

    def _results_to_binary_file(self, results: dict[str, Any], fields: list[str]) -> BytesIO:
        """Given a JSON string containing inference results and the fields
        we want to read from it, generate a binary file (as a BytesIO
        object) to be passed to the fastapi UploadFile method.
        """
        dataset = {k: v for k, v in results.items() if k in fields}

        # Create a CSV in memory
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer)
        csv_writer.writerow(dataset.keys())
        csv_writer.writerows(zip(*dataset.values()))

        # Create a binary file from the CSV, since the upload function expects a binary file
        bin_data = BytesIO(csv_buffer.getvalue().encode("utf-8"))

        return bin_data

    def _add_dataset_to_db(
        self,
        job_id: UUID,
        request: JobCreate,
        s3_file_system: S3FileSystem,
        dataset_filename: str,
        is_gt_generated: bool = True,
    ) -> UUID:
        """Attempts to add the result of a job (generated dataset) as a new dataset in Lumigator.

        :param job_id: The ID of the job, used to identify the S3 path
        :param request: The job request containing the dataset and output fields
        :param s3_file_system: The S3 filesystem dependency for accessing storage
        :return: The ID of the dataset that was created
        :raises DatasetNotFoundError: If the dataset in the request does not exist
        :raises DatasetSizeError: if the dataset is too large
        :raises DatasetInvalidError: if the dataset is invalid
        :raises DatasetMissingFieldsError: if the dataset is missing any of the required fields
        :raises DatasetUpstreamError: if there is an exception interacting with S3
        """
        # Get the dataset from the S3 bucket
        results = self._validate_results(job_id, s3_file_system)

        # make sure the artifacts are present in the results
        required_keys = {"examples", "ground_truth", request.job_config.output_field}
        missing_keys = required_keys - set(results.artifacts.keys())
        if missing_keys:
            raise DatasetMissingFieldsError(set(missing_keys)) from None

        dataset_to_save = {
            "examples": results.artifacts["examples"],
            "ground_truth": results.artifacts["ground_truth"],
            request.job_config.output_field: results.artifacts[request.job_config.output_field],
        }

        bin_data = self._results_to_binary_file(dataset_to_save, list(dataset_to_save.keys()))
        bin_data_size = len(bin_data.getvalue())

        upload_file = UploadFile(
            file=bin_data,
            size=bin_data_size,
            filename=dataset_filename,
            headers=Headers({"content-type": "text/csv"}),
        )
        dataset_record = self._dataset_service.upload_dataset(
            upload_file,
            format=DatasetFormat.JOB,
            run_id=job_id,
            generated=is_gt_generated,
            generated_by=results.artifacts["model"],
        )

        loguru.logger.info(f"Dataset '{dataset_filename}' with ID '{dataset_record.id}' added to the database.")
        return dataset_record.id

    def _validate_results(self, job_id: UUID, s3_file_system: S3FileSystem) -> JobResultObject:
        """Retrieves a job's results from S3 and validates they conform to the ``JobResultObject`` schema.

        Args:
            job_id (UUID): The unique identifier of the job.
            s3_file_system (S3FileSystem): The S3 file system object used to interact with the S3 bucket.

        Raises: ``ValidationError`` if the results do not conform to the schema.
        """
        result_path = self._get_s3_uri(job_id)
        with s3_file_system.open(result_path, "r") as f:
            data = f.read()
            return JobResultObject.model_validate_json(data)

    def get_upstream_job_status(self, job_id: UUID) -> str:
        """Returns the (lowercase) status of the upstream job.

        Example: pending, running, stopped, succeeded, failed.

        :param job_id: The ID of the job to retrieve the status for.
        :return: The status of the upstream job.
        :raises JobNotFoundError: If the job cannot be found in the upstream service.
        :raises JobUpstreamError: If there is an error with the upstream service returning the job status
        """
        try:
            status_response = self._ray_client.get_job_status(str(job_id))
            return str(status_response.value.lower())
        except RuntimeError as e:
            # See: https://github.com/ray-project/ray/blob/24ad12d81f8201859f2f00919929e00a750fa4d2/python/ray/dashboard/modules/dashboard_sdk.py#L282-L285
            if "status code 404" in str(e):
                raise JobNotFoundError(job_id, "Job not found in upstream Ray service") from e
            raise JobUpstreamError("ray", "error getting Ray job status") from e

    def get_job_logs(self, job_id: UUID) -> JobLogsResponse:
        """Retrieves the logs for a job from the upstream service.

        :param job_id: The ID of the job to retrieve logs for.
        :return: The logs for the job.
        :raises JobNotFoundError: If the job cannot be found.
        :raises JobUpstreamError: If there is an error with the upstream service returning the job logs,
                and there are no logs currently persisted in Lumigator's storage.
        """
        job = self._job_repo.get(job_id)
        if not job:
            raise JobNotFoundError(job_id) from None

        try:
            ray_job_logs = self._retrieve_job_logs(job_id)
        except JobUpstreamError as e:
            # If we have logs stored, just return them to support 'offline' Ray
            if job.logs:
                loguru.logger.error("Unable to retrieve job logs from Ray, returning stored DB logs: {}", e)
                return JobLogsResponse(logs=job.logs)
            raise

        # Update the database with the latest logs
        if job.logs != ray_job_logs.logs:
            self._update_job_record(job_id, logs=ray_job_logs.logs)

        return ray_job_logs

    def _retrieve_job_logs(self, job_id: UUID) -> JobLogsResponse:
        resp = requests.get(urljoin(settings.RAY_JOBS_URL, f"{job_id}/logs"), timeout=5)  # 5 seconds
        if resp.status_code == HTTPStatus.NOT_FOUND:
            raise JobUpstreamError("ray", "job_id not found when retrieving logs") from None
        elif resp.status_code != HTTPStatus.OK:
            raise JobUpstreamError(
                "ray",
                f"Unexpected status code getting job logs: {resp.status_code}, error: {resp.text or ''}",
            ) from None
        try:
            metadata = json.loads(resp.text)
            return JobLogsResponse(**metadata)
        except json.JSONDecodeError as e:
            raise JobUpstreamError("ray", f"JSON decode error from {resp.text or ''}") from e

    async def wait_for_job_complete(self, job_id, max_wait_time_sec):
        """Waits for a job to complete, or until a maximum wait time is reached.

        :param job_id: The ID of the job to wait for.
        :param max_wait_time_sec: The maximum time in seconds to wait for the job to complete.
        :return: The status of the job when it completes.
        :rtype: str
        :raises JobUpstreamError: If there is an error with the upstream service returning the
                                  job status
        """
        loguru.logger.info(f"Waiting for job {job_id} to complete...")
        # Get the initial job status
        job_status = self.get_upstream_job_status(job_id)

        # Wait for the job to complete
        elapsed_time = 0
        while job_status not in self.TERMINAL_STATUS:
            if elapsed_time >= max_wait_time_sec:
                loguru.logger.info(f"Job {job_id} did not complete within the maximum wait time.")
                break
            await asyncio.sleep(5)
            elapsed_time += 5
            job_status = self.get_upstream_job_status(job_id)

        # Once the job is finished, retrieve the log and store it in the internal db
        self.get_job_logs(job_id)

        return job_status

    async def handle_annotation_job(self, job_id: UUID, request: JobCreate, max_wait_time_sec: int):
        """Long term we maybe want to move logic about how to handle a specific job
        to be separate from the job service. However, for now, we will keep it here.
        This function can be attached to the jobs that run inference so that the results will
        get added to the dataset db. The job routes that store the results
        in the db will add this function as a background task after the job is created.
        """
        # Figure out the dataset filename
        dataset_filename = self._dataset_service.get_dataset(dataset_id=request.dataset).filename
        dataset_filename = Path(dataset_filename).stem
        dataset_filename = f"{dataset_filename}-annotated.csv"

        job_status = await self.wait_for_job_complete(job_id, max_wait_time_sec)
        if job_status == JobStatus.SUCCEEDED.value:
            self._add_dataset_to_db(
                job_id=job_id,
                request=request,
                s3_file_system=self._dataset_service.s3_filesystem,
                dataset_filename=dataset_filename,
            )
        else:
            loguru.logger.warning(f"Job {job_id} failed, results not stored in DB")

    def add_background_task(self, background_tasks: BackgroundTasks, task: callable, *args):
        """Adds a background task to the background tasks queue."""
        background_tasks.add_task(task, *args)

    def create_job(
        self,
        request: JobCreate,
    ) -> JobResponse:
        """Creates a new evaluation workload to run on Ray and returns the response status.

        :param request: The job creation request.
        :return: The job response.
        :raises JobTypeUnsupportedError: If the job type is not supported.
        :raises JobValidationError: If the secret key identifying the API key required for the job is not found.
        """
        # Typing won't allow other job_type's
        job_type = request.job_config.job_type
        # Prepare the job configuration that will be sent to submit the ray job.
        # This includes both the command that is going to be executed and its
        # arguments defined in eval_config_args
        try:
            job_settings = job_settings_map[job_type]
        except KeyError:
            raise JobTypeUnsupportedError("Unknown job type") from None

        # If we need a secret key that doesn't exist in Lumigator, there's no point in continuing.
        secret_name = getattr(request.job_config, "secret_key_name", None)
        if secret_name and not self._secret_service.is_secret_configured(secret_name):
            raise JobValidationError(
                f"Cannot create job '{request.name}': Requested secret key '{secret_name}' is not configured."
            ) from None

        # Create a db record for the job
        # To find the experiment that a job belongs to,
        # we'd use https://mlflow.org/docs/latest/python_api/mlflow.client.html#mlflow.client.MlflowClient.search_runs
        record = self._job_repo.create(name=request.name, description=request.description, job_type=job_type)
        job_result_storage_path = self._get_s3_uri(record.id)
        dataset_s3_path = self._dataset_service.get_dataset_s3_path(request.dataset)
        job_config = job_settings.generate_config(request, record.id, dataset_s3_path, job_result_storage_path)

        # Build runtime ENV for workers
        runtime_env_vars = settings.with_ray_worker_env_vars({"MZAI_JOB_ID": str(record.id)})

        # Include requested secrets (API keys) from stored secrets.
        if secret_name:
            try:
                value = self._secret_service.get_decrypted_secret_value(secret_name)
            except (SecretNotFoundError, SecretDecryptionError) as e:
                raise JobValidationError(f"Error configuring secret for job: {record.id}, name: {request.name}") from e

            # Add the secret to the runtime env vars using 'api_key' to identify it in jobs.
            runtime_env_vars["api_key"] = value

        # eval_config_args is used to map input configuration parameters with
        # command parameters provided via command line to the ray job.
        # To do this, we use a dict where keys are parameter names as they'd
        # appear on the command line and the values are the respective params.
        job_config_args = {
            "--config": job_config.model_dump_json(),
        }

        ray_config = JobConfig(
            job_id=record.id,
            job_type=job_type,
            command=job_settings.command,
            args=job_config_args,
        )

        runtime_env = {
            "pip": job_settings.pip_reqs,
            "working_dir": job_settings.work_dir,
            # FIXME move to a constant
            "py_modules": ["../schemas/lumigator_schemas"],
            "env_vars": runtime_env_vars,
        }

        metadata = {"job_type": job_type}

        entrypoint = RayJobEntrypoint(
            config=ray_config,
            metadata=metadata,
            runtime_env=runtime_env,
            num_gpus=settings.RAY_WORKER_GPUS,
        )
        loguru.logger.info(f"Submitting {job_type} Ray job...")
        submit_ray_job(self._ray_client, entrypoint)

        # NOTE: Only inference jobs can store results in a dataset atm. Among them:
        # - prediction jobs are run in a workflow before evaluations => they trigger dataset saving
        #   at workflow level so it is prepended to the eval job
        # - annotation jobs do not run in workflows => they trigger dataset saving here at job level
        # As JobType.ANNOTATION is not used uniformly throughout our code yet, we rely on the already
        # existing `store_to_dataset` parameter to explicitly trigger this in the annotation case
        if job_type != JobType.EVALUATION and getattr(request.job_config, "store_to_dataset", False):
            self.add_background_task(
                self._background_tasks,
                self.handle_annotation_job,
                record.id,
                request,
                DEFAULT_POST_INFER_JOB_TIMEOUT_SEC,
            )

        return JobResponse.model_validate(record)

    def get_job(self, job_id: UUID) -> JobResponse:
        """Gets a job from the repository (database) by ID.

        :param job_id: the ID of the job to retrieve
        :return: the job record which includes information on whether a job belongs to an experiment
        :rtype: JobRecord
        :raises JobNotFoundError: If the job does not exist
        :raises JobUpstreamError: If there is an error with the upstream service returning the latest job status.
        """
        record = self._get_job_record(job_id)
        loguru.logger.info(f"Obtained info for job ID: {job_id} name: {record.name}")

        # If the job is finished (successfully or not), return the record.
        if record.status.value in self.TERMINAL_STATUS:
            return JobResponse.model_validate(record)

        # Attempt to get the latest job status from the upstream service.
        job_status = self.get_upstream_job_status(job_id)

        # Update job status in the DB if it differs from the current status
        if job_status != record.status.value.lower():
            record = self._update_job_record(job_id, status=job_status)

        return JobResponse.model_validate(record)

    def list_jobs(
        self,
        skip: int = DEFAULT_SKIP,
        limit: int = DEFAULT_LIMIT,
        job_types: list[str] = (),
    ) -> ListingResponse[JobResponse]:
        # It would be better if we could just feed an empty dict,
        # but this complicates things at the ORM level,
        # see https://docs.sqlalchemy.org/en/20/core/sqlelement.html#sqlalchemy.sql.expression.or_
        records = self._job_repo.list(
            skip,
            limit,
            criteria=[or_(*[JobRecord.job_type == job_type for job_type in job_types])],
        )
        total = len(records)
        return ListingResponse(
            total=total,
            items=[self.get_job(record.id) for record in records],
        )

    def update_job_status(
        self,
        job_id: UUID,
        status: JobStatus,
    ) -> JobResponse:
        """Updates the status of a job.

        :param job_id: the ID of the job to update
        :param status: the status to update the job with
        :return: the updated job information
        :rtype: JobResponse
        :raises JobNotFoundError: If the job does not exist
        """
        record = self._update_job_record(job_id, status=status)
        return JobResponse.model_validate(record)

    def get_job_result(self, job_id: UUID) -> JobResultResponse:
        """Return job results metadata if available in the DB.

        :param job_id: the ID of the job to retrieve results for
        :return: the job results metadata
        :rtype: JobResultResponse
        :raises JobNotFoundError: if the job does not exist
        """
        result_record = self._result_repo.get_by_job_id(job_id)
        if result_record is None:
            raise JobNotFoundError(job_id) from None

        return JobResultResponse.model_validate(result_record)

    async def get_job_result_download(self, job_id: UUID) -> JobResultDownloadResponse:
        """Return job results file URL for downloading."""
        # Generate presigned download URL for the object
        result_key = self._get_results_s3_key(job_id)

        download_url = await self._dataset_service.s3_filesystem.s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": result_key,
            },
            ExpiresIn=settings.S3_URL_EXPIRATION,
        )
        return JobResultDownloadResponse(id=job_id, download_url=download_url)

    def sanitize_job_name(self, job_name: str) -> str:
        """Sanitize a job name to be S3-safe.

        :param job_name: The job name to sanitize.
        :return: The sanitized job name.
        """
        return re.sub(self.SAFE_JOB_NAME_REGEX, self.JOB_NAME_REPLACEMENT_CHAR, job_name)
