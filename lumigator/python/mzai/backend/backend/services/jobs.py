import csv
import json
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any
from uuid import UUID

import loguru

# TODO: the evaluator_lite import will need to be renamed to evaluator
#   once the new experiments API is merged
from evaluator_lite.schemas import EvalJobConfig, EvalJobOutput
from fastapi import BackgroundTasks, UploadFile
from inference.schemas import InferenceJobConfig, InferenceJobOutput
from lumigator_schemas.datasets import DatasetFormat
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    JobConfig,
    JobEvalCreate,
    JobEvalLiteCreate,
    JobInferenceCreate,
    JobResponse,
    JobResultDownloadResponse,
    JobResultResponse,
    JobStatus,
    JobType,
)
from pydantic import BaseModel
from ray.job_submission import JobSubmissionClient
from s3fs import S3FileSystem

from backend import config_templates
from backend.ray_submit.submission import RayJobEntrypoint, submit_ray_job
from backend.records.jobs import JobRecord
from backend.repositories.jobs import JobRepository, JobResultRepository
from backend.services.datasets import DatasetService
from backend.services.exceptions.job_exceptions import (
    JobNotFoundError,
    JobTypeUnsupportedError,
    JobUpstreamError,
)
from backend.settings import settings


class JobService:
    # set storage path
    storage_path = f"s3://{Path(settings.S3_BUCKET) / settings.S3_JOB_RESULTS_PREFIX}/"

    job_settings = {
        JobType.INFERENCE: {
            "command": settings.INFERENCE_COMMAND,
            "pip": settings.INFERENCE_PIP_REQS,
            "work_dir": settings.INFERENCE_WORK_DIR,
            "ray_worker_gpus_fraction": settings.RAY_WORKER_GPUS_FRACTION,
            "ray_worker_gpus": settings.RAY_WORKER_GPUS,
        },
        JobType.EVALUATION: {
            "command": settings.EVALUATOR_COMMAND,
            "pip": settings.EVALUATOR_PIP_REQS,
            "work_dir": settings.EVALUATOR_WORK_DIR,
            "ray_worker_gpus_fraction": settings.RAY_WORKER_GPUS_FRACTION,
            "ray_worker_gpus": settings.RAY_WORKER_GPUS,
        },
        JobType.EVALUATION_LITE: {
            "command": settings.EVALUATOR_LITE_COMMAND,
            "pip": settings.EVALUATOR_LITE_PIP_REQS,
            "work_dir": settings.EVALUATOR_LITE_WORK_DIR,
            "ray_worker_gpus_fraction": settings.RAY_WORKER_GPUS_FRACTION,
            "ray_worker_gpus": settings.RAY_WORKER_GPUS,
        },
    }

    def __init__(
        self,
        job_repo: JobRepository,
        result_repo: JobResultRepository,
        ray_client: JobSubmissionClient,
        dataset_service: DatasetService,
    ):
        self.job_repo = job_repo
        self.result_repo = result_repo
        self.ray_client = ray_client
        self._dataset_service = dataset_service

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

    def _add_dataset_to_db(self, job_id: UUID, request: JobInferenceCreate, s3: S3FileSystem):
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
        result_key = self._get_results_s3_key(job_id)
        with s3.open(f"{settings.S3_BUCKET}/{result_key}", "r") as f:
            # Validate that the output file adheres to the expected inference output schema
            results = InferenceJobOutput.model_validate(json.loads(f.read()))

        # define the fields we want to keep from the results JSON
        # and build a CSV file from it as a BytesIO object
        fields = ["examples", "ground_truth", request.output_field]
        bin_data = self._results_to_binary_file(results.model_dump(), fields)
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
            generated_by=results.model,
        )

        loguru.logger.info(
            f"Dataset '{dataset_filename}' with ID '{dataset_record.id}' added to the database."
        )

    def _validate_evaluation_results(
        self, job_id: UUID, request: JobEvalLiteCreate, s3: S3FileSystem
    ):
        """Handles the evaluation result for a given job.

        Args:
            job_id (UUID): The unique identifier of the job.
            request (JobEvalLiteCreate): The request object containing job evaluation details.
            s3 (S3FileSystem): The S3 file system object used to interact with the S3 bucket.

        Note:
            Currently, this function only validates the evaluation result. Future implementations
            may include storing the results in a database (e.g., mlflow).
        """
        loguru.logger.info("Handling evaluation result")

        result_key = self._get_results_s3_key(job_id)
        with s3.open(f"{settings.S3_BUCKET}/{result_key}", "r") as f:
            EvalJobOutput.model_validate(json.loads(f.read()))

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

    def _get_config_template(self, job_type: str, model_name: str) -> str:
        job_templates = config_templates.templates[job_type]

        if model_name in job_templates:
            # if no config template is provided, get the default one for the model
            config_template = job_templates[model_name]
        else:
            # if no default config template is provided, get the causal template
            # (which works with seq2seq models too except it does not use pipeline)
            config_template = job_templates["default"]

        return config_template

    def _set_model_type(self, request: BaseModel) -> str:
        """Sets model URL based on protocol address"""
        if request.model.startswith("oai://"):
            model_url = settings.OAI_API_URL
        elif request.model.startswith("mistral://"):
            model_url = settings.MISTRAL_API_URL
        else:
            model_url = request.model_url

        return model_url

    def _validate_config(self, job_type: str, config_template: str, config_params: dict):
        if job_type == JobType.INFERENCE:
            InferenceJobConfig.model_validate_json(config_template.format(**config_params))
        elif job_type == JobType.EVALUATION_LITE:
            EvalJobConfig.model_validate_json(config_template.format(**config_params))
        else:
            loguru.logger.info(f"Validation for job type {job_type} not yet supported.")

    def _get_job_params(self, job_type: JobType, record, request: BaseModel) -> dict:
        # get dataset S3 path from UUID
        dataset_s3_path = self._dataset_service.get_dataset_s3_path(request.dataset)

        # provide a reasonable system prompt for services where none was specified
        if (
            job_type in [JobType.EVALUATION, JobType.INFERENCE]
            and request.system_prompt is None
            and not request.model.startswith("hf://")
        ):
            request.system_prompt = settings.DEFAULT_SUMMARIZER_PROMPT

        # Base job parameters (used for eval-lite, evaluation and inference).
        job_params = {
            "dataset_path": dataset_s3_path,
            "job_id": record.id,
            "job_name": request.name,
            "max_samples": request.max_samples,
            "model_uri": request.model,
            "storage_path": self.storage_path,
        }

        # this section differs between inference and eval
        if job_type == JobType.EVALUATION:
            job_params = job_params | {
                "model_url": self._set_model_type(request),
                "skip_inference": request.skip_inference,
                "system_prompt": request.system_prompt,
            }
        elif job_type == JobType.INFERENCE:
            job_params = job_params | {
                "accelerator": request.accelerator,
                "frequency_penalty": request.frequency_penalty,
                "max_tokens": request.max_tokens,
                "model_url": self._set_model_type(request),
                "output_field": request.output_field,
                "revision": request.revision,
                "system_prompt": request.system_prompt,
                "task": request.task,
                "temperature": request.temperature,
                "top_p": request.top_p,
                "torch_dtype": request.torch_dtype,
                "trust_remote_code": request.trust_remote_code,
                "use_fast": request.use_fast,
            }

        return job_params

    def create_job(
        self,
        request: JobEvalCreate | JobEvalLiteCreate | JobInferenceCreate,
        background_tasks: BackgroundTasks,
        experiment_id: UUID = None,
    ) -> JobResponse:
        """Creates a new workload to run on Ray based on the type of request.

        :param request: contains information on the requested job, including type,
                        (e.g. inference or evaluation)
        :param background_tasks: dependency used to initiate tasks in the background
        :param experiment_id: experiment ID (optional) links this job to a parent experiment.
        :return: information on the created job
        :rtype: JobResponse
        :raises JobTypeUnsupportedError: if the requested job type is not supported
        """
        if isinstance(request, JobEvalCreate):
            job_type = JobType.EVALUATION
        elif isinstance(request, JobEvalLiteCreate):
            job_type = JobType.EVALUATION_LITE
        elif isinstance(request, JobInferenceCreate):
            job_type = JobType.INFERENCE
            if not request.output_field:
                request.output_field = "predictions"
        else:
            raise JobTypeUnsupportedError(request) from None

        # Create a db record for the job
        record = self.job_repo.create(
            name=request.name, description=request.description, experiment_id=experiment_id
        )

        # prepare configuration parameters, which depend both on the user inputs
        # (request) and on the job type
        config_params = self._get_job_params(job_type, record, request)

        loguru.logger.info(f"sending config_params...{config_params}")

        # load a config template and fill it up with config_params
        if request.config_template is not None and request.config_template != "":
            config_template = request.config_template
        else:
            config_template = self._get_config_template(job_type, request.model)

        loguru.logger.info(f"template...{config_template, job_type, request.model}")

        self._validate_config(job_type, config_template, config_params)

        # eval_config_args is used to map input configuration parameters with
        # command parameters provided via command line to the ray job.
        # To do this, we use a dict where keys are parameter names as they'd
        # appear on the command line and the values are the respective params.
        job_config_args = {
            "--config": config_template.format(**config_params),
        }

        # Prepare the job configuration that will be sent to submit the ray job.
        # This includes both the command that is going to be executed and its
        # arguments defined in eval_config_args
        job_settings = self.job_settings[job_type]

        ray_config = JobConfig(
            job_id=record.id,
            job_type=job_type,
            command=job_settings["command"],
            args=job_config_args,
        )

        # build runtime ENV for workers
        runtime_env_vars = {"MZAI_JOB_ID": str(record.id)}
        settings.inherit_ray_env(runtime_env_vars)

        # set num_gpus per worker (zero if we are just hitting a service)
        if not request.model.startswith("hf://"):
            worker_gpus = job_settings["ray_worker_gpus_fraction"]
        else:
            worker_gpus = job_settings["ray_worker_gpus"]

        runtime_env = {
            "pip": job_settings["pip"],
            "working_dir": job_settings["work_dir"],
            "env_vars": runtime_env_vars,
        }

        metadata = {"job_type": job_type}

        loguru.logger.info("runtime env setup...")
        loguru.logger.info(f"{runtime_env}")

        entrypoint = RayJobEntrypoint(
            config=ray_config, metadata=metadata, runtime_env=runtime_env, num_gpus=worker_gpus
        )
        loguru.logger.info("Submitting {job_type} Ray job...")
        submit_ray_job(self.ray_client, entrypoint)

        # Inference jobs produce a new dataset
        # Add the dataset to the (local) database
        if job_type == JobType.INFERENCE and request.store_to_dataset:
            background_tasks.add_task(
                self.on_job_complete,
                record.id,
                self._add_dataset_to_db,
                record.id,
                JobInferenceCreate.model_validate(request),
                self._dataset_service.s3_filesystem,
            )
        elif job_type == JobType.EVALUATION_LITE:
            background_tasks.add_task(
                self.on_job_complete,
                record.id,
                self._validate_evaluation_results,
                record.id,
                JobEvalLiteCreate.model_validate(request),
                self._dataset_service.s3_filesystem,
            )
        # FIXME The ray status is now _not enough_ to set the job status,
        # since the dataset may still be under creation

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
        skip: int = 0,
        limit: int = 100,
    ) -> ListingResponse[JobResponse]:
        total = self.job_repo.count()
        records = self.job_repo.list(skip, limit)
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
