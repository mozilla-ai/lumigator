import asyncio
import csv
import json
from abc import ABC, abstractmethod
from http import HTTPStatus
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any
from urllib.parse import urljoin
from uuid import UUID

import loguru
import requests
from evaluator.schemas import DatasetConfig as ELDatasetConfig
from evaluator.schemas import EvalJobConfig, EvaluationConfig
from fastapi import BackgroundTasks, UploadFile
from inference.schemas import DatasetConfig as IDatasetConfig
from inference.schemas import (
    GenerationConfig,
    HuggingFacePipelineConfig,
    InferenceJobConfig,
    InferenceServerConfig,
)
from inference.schemas import JobConfig as InferJobConfig
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
from pydantic import BaseModel
from ray.job_submission import JobSubmissionClient
from s3fs import S3FileSystem
from sqlalchemy.sql.expression import or_

from backend.ray_submit.submission import RayJobEntrypoint, submit_ray_job
from backend.records.jobs import JobRecord
from backend.repositories.jobs import JobRepository, JobResultRepository
from backend.services.datasets import DatasetService
from backend.services.exceptions.dataset_exceptions import DatasetMissingFieldsError
from backend.services.exceptions.job_exceptions import (
    JobNotFoundError,
    JobTypeUnsupportedError,
    JobUpstreamError,
)
from backend.settings import settings

DEFAULT_SKIP = 0
DEFAULT_LIMIT = 100
JobSpecificRestrictedConfig = type[JobEvalConfig | JobInferenceConfig]


# The end result should be that InferenceJobConfig is actually JobInferenceConfig
# (resp. Eval)
# For the moment, something will convert one into the other, and we'll decide where
# to put this. The jobs should ideally have no dependency towards the backend.


class JobDefinition(ABC):
    """Abstract base class for jobs.

    Attributes:
    ----------
    command : str
        The command to execute the job.
    pip_reqs : str, optional
        Path to a requirements file specifying dependencies (default: None).
    work_dir : str, optional
        Working directory for the job (default: None).
    ray_worker_gpus_fraction : float
        Fraction of a GPU allocated per Ray worker.
    ray_worker_gpus : float
        Number of GPUs allocated per Ray worker.
    config_model : BaseModel
        Pydantic model representing job-specific configuration.

    """

    command: str
    pip_reqs: str | None
    work_dir: str | None
    ray_worker_gpus_fraction: float
    ray_worker_gpus: float
    config_model: BaseModel

    # This should end up not being necessary, since we'd expose the whole job config
    @abstractmethod
    def generate_config(self, request: JobCreate, record_id: UUID, dataset_path: str, storage_path: str) -> BaseModel:
        """Generates

        Parameters
        ----------
        request : JobCreate
            Non-job-specific parameters for job creation
        record_id : UUID
            Job ID assigned to the job
        dataset_path : str
            S3 path for the input dataset
        storage_path : str
            S3 where the backend will store the results from the job

        Returns:
        -------
        generate_config : BaseModel
            A job-specific pydantic model that will be sent to the Ray job instance
        """
        pass

    @abstractmethod
    def store_as_dataset(self) -> bool:
        """Returns:
        -------
        store_as_dataset : bool
            Whether the results should be stored in an S3 path
        """
        pass

    def __init__(self, command, pip_reqs, work_dir, ray_worker_gpus_fraction, ray_worker_gpus, config_model):
        self.command = command
        self.pip_reqs = pip_reqs
        self.work_dir = work_dir
        self.ray_worker_gpus_fraction = ray_worker_gpus_fraction
        self.ray_worker_gpus = ray_worker_gpus
        self.config_model = config_model


class JobDefinitionInference(JobDefinition):
    def generate_config(self, request: JobCreate, record_id: UUID, dataset_path: str, storage_path: str):
        job_config = InferenceJobConfig(
            name=f"{request.name}/{record_id}",
            dataset=IDatasetConfig(path=dataset_path),
            job=InferJobConfig(
                max_samples=request.max_samples,
                storage_path=storage_path,
                # TODO Should be unnecessary, check
                output_field=request.job_config.output_field or "predictions",
            ),
            system_prompt=request.job_config.task_definition.system_prompt,
        )
        if request.job_config.provider == "hf":
            # Custom logic: if provider is hf, we run the hf model inside the ray job
            job_config.hf_pipeline = HuggingFacePipelineConfig(
                model_name_or_path=request.job_config.model,
                task=request.job_config.task_definition.task,
                accelerator=request.job_config.accelerator,
                revision=request.job_config.revision,
                use_fast=request.job_config.use_fast,
                trust_remote_code=request.job_config.trust_remote_code,
                torch_dtype=request.job_config.torch_dtype,
                max_new_tokens=500,
            )
        else:
            # It will be a pass through to LiteLLM
            job_config.inference_server = InferenceServerConfig(
                base_url=request.job_config.base_url if request.job_config.base_url else None,
                model=request.job_config.model,
                provider=request.job_config.provider,
                system_prompt=request.job_config.task_definition.system_prompt,
                max_retries=3,
            )
        job_config.generation_config = GenerationConfig(
            max_tokens=request.job_config.max_tokens,
            frequency_penalty=request.job_config.frequency_penalty,
            temperature=request.job_config.temperature,
            top_p=request.job_config.top_p,
        )
        return job_config

    def store_as_dataset(self) -> bool:
        return True


class JobDefinitionEvaluation(JobDefinition):
    def generate_config(self, request: JobCreate, record_id: UUID, dataset_path: str, storage_path: str):
        job_config = EvalJobConfig(
            name=f"{request.name}/{record_id}",
            dataset=ELDatasetConfig(path=dataset_path),
            evaluation=EvaluationConfig(
                metrics=request.job_config.metrics,
                max_samples=request.max_samples,
                return_input_data=True,
                return_predictions=True,
                storage_path=storage_path,
            ),
        )
        return job_config

    def store_as_dataset(self) -> bool:
        return False


class JobService:
    # set storage path
    storage_path = f"s3://{Path(settings.S3_BUCKET) / settings.S3_JOB_RESULTS_PREFIX}/"

    job_settings = {
        JobType.INFERENCE: JobDefinitionInference(
            command=settings.INFERENCE_COMMAND,
            pip_reqs=settings.INFERENCE_PIP_REQS,
            work_dir=settings.INFERENCE_WORK_DIR,
            ray_worker_gpus_fraction=settings.RAY_WORKER_GPUS_FRACTION,
            ray_worker_gpus=settings.RAY_WORKER_GPUS,
            config_model=InferenceJobConfig,
        ),
        JobType.EVALUATION: JobDefinitionEvaluation(
            command=settings.EVALUATOR_COMMAND,
            pip_reqs=settings.EVALUATOR_PIP_REQS,
            work_dir=settings.EVALUATOR_WORK_DIR,
            ray_worker_gpus_fraction=settings.RAY_WORKER_GPUS_FRACTION,
            ray_worker_gpus=settings.RAY_WORKER_GPUS,
            config_model=EvalJobConfig,
        ),
    }

    NON_TERMINAL_STATUS = [
        JobStatus.CREATED.value,
        JobStatus.PENDING.value,
        JobStatus.RUNNING.value,
    ]
    """list: A list of non-terminal job statuses."""

    # TODO: rely on https://github.com/ray-project/ray/blob/7c2a200ef84f17418666dad43017a82f782596a3/python/ray/dashboard/modules/job/common.py#L53
    TERMINAL_STATUS = [JobStatus.FAILED.value, JobStatus.SUCCEEDED.value]
    """list: A list of terminal job statuses."""

    def __init__(
        self,
        job_repo: JobRepository,
        result_repo: JobResultRepository,
        ray_client: JobSubmissionClient,
        dataset_service: DatasetService,
        background_tasks: BackgroundTasks,
    ):
        self.job_repo = job_repo
        self.result_repo = result_repo
        self.ray_client = ray_client
        self._dataset_service = dataset_service
        self._background_tasks = background_tasks

    def _get_job_record_per_type(self, job_type: str) -> list[JobRecord]:
        records = self.job_repo.get_by_job_type(job_type)
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
        record = self.job_repo.get(job_id)
        if record is None:
            raise JobNotFoundError(job_id) from None

        return record

    def _update_job_record(self, job_id: UUID, **updates) -> JobRecord:
        """Updates an existing job record in the repository (database) by ID.

        :param job_id: The ID of the job to update
        :param updates: The updates to update the job record
        :return: The updated job record
        :rtype: JobRecord
        :raises JobNotFoundError: If the job does not exist in the database
        """
        record = self.job_repo.update(job_id, **updates)
        if record is None:
            raise JobNotFoundError(job_id) from None

        return record

    def _get_results_s3_key(self, job_id: UUID) -> str:
        """Given a job ID, returns the S3 key identifying where job results should be stored.

        The S3 key is constructed from:
        - settings.S3_JOB_RESULTS_PREFIX: the path where jobs are stored
        - settings.S3_JOB_RESULTS_FILENAME: a filename template that is to be formatted with some of
         the job record's metadata (e.g. exp name/id)

        :param job_id: The ID of the job to retrieve the S3 key for
        :return: The returned string contains the S3 key *excluding the bucket / s3 prefix*,
        as it is to be used by the boto3 client which accepts them separately.
        :rtype: str
        """
        record = self._get_job_record(job_id)

        return str(
            Path(settings.S3_JOB_RESULTS_PREFIX)
            / settings.S3_JOB_RESULTS_FILENAME.format(job_name=record.name, job_id=record.id)
        )

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

    def _add_dataset_to_db(self, job_id: UUID, request: JobCreate, s3: S3FileSystem):
        """Attempts to add the result of a job (generated dataset) as a new dataset in Lumigator.

        :param job_id: The ID of the job, used to identify the S3 path
        :param request: The job request containing the dataset and output fields
        :param s3: The S3 filesystem dependency for accessing storage
        :raises DatasetNotFoundError: If the dataset in the request does not exist
        :raises DatasetSizeError: if the dataset is too large
        :raises DatasetInvalidError: if the dataset is invalid
        :raises DatasetMissingFieldsError: if the dataset is missing any of the required fields
        :raises DatasetUpstreamError: if there is an exception interacting with S3
        """
        loguru.logger.info("Adding a new dataset entry to the database...")

        # Get the dataset from the S3 bucket
        results = self._validate_results(job_id, s3)

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

        # Figure out the dataset filename
        dataset_filename = self._dataset_service.get_dataset(dataset_id=request.dataset).filename
        dataset_filename = Path(dataset_filename).stem
        dataset_filename = f"{dataset_filename}-annotated.csv"

        upload_file = UploadFile(
            file=bin_data,
            size=bin_data_size,
            filename=dataset_filename,
            headers={"content-type": "text/csv"},
        )
        dataset_record = self._dataset_service.upload_dataset(
            upload_file,
            format=DatasetFormat.JOB,
            run_id=job_id,
            generated=True,
            generated_by=results.artifacts["model"],
        )

        loguru.logger.info(f"Dataset '{dataset_filename}' with ID '{dataset_record.id}' added to the database.")

    def _validate_results(self, job_id: UUID, s3: S3FileSystem) -> JobResultObject:
        """Handles the evaluation result for a given job.

        Args:
            job_id (UUID): The unique identifier of the job.
            s3 (S3FileSystem): The S3 file system object used to interact with the S3 bucket.

        Note:
            Currently, this function only validates the evaluation result. Future implementations
            may include storing the results in a database (e.g., mlflow).
        """
        loguru.logger.info("Handling evaluation result")

        result_key = self._get_results_s3_key(job_id)
        with s3.open(f"{settings.S3_BUCKET}/{result_key}", "r") as f:
            return JobResultObject.model_validate(json.loads(f.read()))

    def get_upstream_job_status(self, job_id: UUID) -> str:
        """Returns the (lowercase) status of the upstream job.

        Example: PENDING, RUNNING, STOPPED, SUCCEEDED, FAILED.

        :param job_id: The ID of the job to retrieve the status for.
        :return: The status of the upstream job.
        :rtype: str
        :raises JobUpstreamError: If there is an error with the upstream service returning the
                                  job status
        """
        try:
            status_response = self.ray_client.get_job_status(str(job_id))
            return str(status_response.value.lower())
        except RuntimeError as e:
            raise JobUpstreamError("ray", "error getting Ray job status", e) from e

    def get_job_logs(self, job_id: UUID) -> JobLogsResponse:
        db_logs = self.job_repo.get(job_id)
        if not db_logs:
            raise JobNotFoundError(job_id, "Failed to find the job record holding the logs") from None
        elif not db_logs.logs:
            ray_db_logs = self.retrieve_job_logs(job_id)
            self._update_job_record(job_id, logs=ray_db_logs.logs)
            return ray_db_logs
        else:
            return JobLogsResponse(logs=db_logs.logs)

    def retrieve_job_logs(self, job_id: UUID) -> JobLogsResponse:
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

    async def wait_for_job_complete(self, job_id, max_wait_time_sec=None):
        """Waits for a job to complete, or until a maximum wait time is reached.

        :param job_id: The ID of the job to wait for.
        :param max_wait_time: The maximum time to wait for the job to complete.
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
            if max_wait_time_sec and elapsed_time >= max_wait_time_sec:
                loguru.logger.info(f"Job {job_id} did not complete within the maximum wait time.")
                break
            await asyncio.sleep(5)
            elapsed_time += 5
            job_status = self.get_upstream_job_status(job_id)

        # Once the job is finished, retrieve the log and store it in the internal db
        self.get_job_logs(job_id)

        return job_status

    async def handle_inference_job(self, job_id: UUID, request: JobCreate):
        """Long term we maybe want to move logic about how to handle a specific job
        to be separate from the job service. However, for now, we will keep it here.
        This function can be attached to the jobs that run inference so that the results will
        get added to the dataset db. The job routes that store the results
        in the db will add this function as a background task after the job is created.
        """
        loguru.logger.info("Handling inference job result")

        await self.wait_for_job_complete(job_id)
        self._add_dataset_to_db(
            job_id,
            request,
            self._dataset_service.s3_filesystem,
        )

    def add_background_task(self, background_tasks: BackgroundTasks, task: callable, *args):
        """Adds a background task to the background tasks queue."""
        background_tasks.add_task(task, *args)

    def create_job(
        self,
        request: JobCreate,
        experiment_id: UUID = None,
    ) -> JobResponse:
        """Creates a new evaluation workload to run on Ray and returns the response status."""
        # Typing won't allow other job_type's
        job_type = request.job_config.job_type
        # Prepare the job configuration that will be sent to submit the ray job.
        # This includes both the command that is going to be executed and its
        # arguments defined in eval_config_args
        try:
            job_settings = self.job_settings[job_type]
        except KeyError as e:
            raise JobTypeUnsupportedError("Unknown job type") from e

        # Create a db record for the job
        # To find the experiment that a job belongs to,
        # we'd use https://mlflow.org/docs/latest/python_api/mlflow.client.html#mlflow.client.MlflowClient.search_runs
        record = self.job_repo.create(name=request.name, description=request.description, job_type=job_type)

        dataset_s3_path = self._dataset_service.get_dataset_s3_path(request.dataset)
        job_config = job_settings.generate_config(request, record.id, dataset_s3_path, self.storage_path)

        # eval_config_args is used to map input configuration parameters with
        # command parameters provided via command line to the ray job.
        # To do this, we use a dict where keys are parameter names as they'd
        # appear on the command line and the values are the respective params.

        # ...and use directly Job*Config(request.job.config.model_dump_json())
        job_config_args = {
            "--config": job_config.model_dump_json(),
        }

        ray_config = JobConfig(
            job_id=record.id,
            job_type=job_type,
            command=job_settings.command,
            args=job_config_args,
        )

        # build runtime ENV for workers
        runtime_env_vars = {"MZAI_JOB_ID": str(record.id)}
        settings.inherit_ray_env(runtime_env_vars)

        runtime_env = {
            "pip": job_settings.pip_reqs,
            "working_dir": job_settings.work_dir,
            "env_vars": runtime_env_vars,
        }

        metadata = {"job_type": job_type}

        loguru.logger.info("runtime env setup...")
        loguru.logger.info(f"{runtime_env}")

        entrypoint = RayJobEntrypoint(
            config=ray_config,
            metadata=metadata,
            runtime_env=runtime_env,
            num_gpus=settings.RAY_WORKER_GPUS,
        )
        loguru.logger.info("Submitting {job_type} Ray job...")
        submit_ray_job(self.ray_client, entrypoint)

        # NOTE: Only inference jobs can store results in a dataset atm. Among them:
        # - prediction jobs are run in a workflow before evaluations => they trigger dataset saving
        #   at workflow level so it is prepended to the eval job
        # - annotation jobs do not run in workflows => they trigger dataset saving here at job level
        # As JobType.ANNOTATION is not used uniformly throughout our code yet, we rely on the already
        # existing `store_to_dataset` parameter to explicitly trigger this in the annotation case
        if job_settings.store_as_dataset():
            self.add_background_task(self._background_tasks, self.handle_inference_job, record.id, request)

        loguru.logger.info("Getting response...")
        return JobResponse.model_validate(record)

    def get_job(self, job_id: UUID) -> JobResponse:
        """Gets a job from the repository (database) by ID.

        :param job_id: the ID of the job to retrieve
        :return: the job record which includes information on whether a job belongs to an experiment
        :rtype: JobRecord
        :raises JobNotFoundError: If the job does not exist
        """
        record = self._get_job_record(job_id)
        loguru.logger.info(f"Obtaining info for job {job_id}: {record.name}")

        if record.status == JobStatus.FAILED or record.status == JobStatus.SUCCEEDED:
            return JobResponse.model_validate(record)

        # get job status from ray
        job_status = self.ray_client.get_job_status(job_id)
        loguru.logger.info(f"Obtaining info from ray for job {job_id}: {job_status}")

        # update job status in the DB if it differs from the current status
        if job_status.lower() != record.status.value.lower():
            record = self._update_job_record(job_id, status=job_status.lower())

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
        records = self.job_repo.list(
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
        result_record = self.result_repo.get_by_job_id(job_id)
        if result_record is None:
            raise JobNotFoundError(job_id) from None

        return JobResultResponse.model_validate(result_record)

    def get_job_result_download(self, job_id: UUID) -> JobResultDownloadResponse:
        """Return job results file URL for downloading."""
        # Generate presigned download URL for the object
        result_key = self._get_results_s3_key(job_id)
        download_url = self._dataset_service.s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": result_key,
            },
            ExpiresIn=settings.S3_URL_EXPIRATION,
        )
        return JobResultDownloadResponse(id=job_id, download_url=download_url)
