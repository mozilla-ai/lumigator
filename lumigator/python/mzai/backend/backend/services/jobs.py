import asyncio
import csv
import json
from collections.abc import Callable
from io import BytesIO, StringIO
from pathlib import Path
from uuid import UUID

import loguru
from fastapi import BackgroundTasks, HTTPException, UploadFile, status
from lumigator_schemas.datasets import DatasetFormat
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    JobConfig,
    JobCreate,
    JobInferenceCreate,
    JobResponse,
    JobResultDownloadResponse,
    JobResultResponse,
    JobStatus,
    JobType,
)
from lumigator_schemas.jobs.inference import InferenceJobConfig
from pydantic import BaseModel
from ray.job_submission import JobSubmissionClient
from s3fs import S3FileSystem

from backend import config_templates
from backend.ray_submit.submission import RayJobEntrypoint, submit_ray_job
from backend.records.jobs import JobRecord
from backend.repositories.jobs import JobRepository, JobResultRepository
from backend.services.datasets import DatasetService
from backend.settings import settings


class JobService:
    # set storage path
    storage_path = f"s3://{ Path(settings.S3_BUCKET) / settings.S3_JOB_RESULTS_PREFIX }/"

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

    def _raise_not_found(self, job_id: UUID):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Job {job_id} not found.")

    def _get_job_record(self, job_id: UUID) -> JobRecord:
        record = self.job_repo.get(job_id)
        if record is None:
            self._raise_not_found(job_id)
        return record

    def _update_job_record(self, job_id: UUID, **updates) -> JobRecord:
        record = self.job_repo.update(job_id, **updates)
        if record is None:
            self._raise_not_found(job_id)
        return record

    def _get_results_s3_key(self, job_id: UUID) -> str:
        """Given an job ID, returns the S3 key for the job results.

        The S3 key is built from:
        - settings.S3_JOB_RESULTS_PREFIX: the path where jobs are stored
        - settings.S3_JOB_RESULTS_FILENAME: a filename template that is to be
          formatted with some of the job record's metadata (e.g. exp name/id)

        The returned string contains the S3 key *excluding the bucket / s3 prefix*,
        as it is to be used by the boto3 client which accepts them separately.
        """
        record = self._get_job_record(job_id)

        return str(
            Path(settings.S3_JOB_RESULTS_PREFIX)
            / settings.S3_JOB_RESULTS_FILENAME.format(job_name=record.name, job_id=record.id)
        )

    def _results_to_binary_file(self, results: str, fields: list[str]) -> BytesIO:
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
        loguru.logger.info("Adding a new dataset entry to the database...")

        # Get the dataset from the S3 bucket
        result_key = self._get_results_s3_key(job_id)
        with s3.open(f"{settings.S3_BUCKET}/{result_key}", "r") as f:
            results = json.loads(f.read())

        # define the fields we want to keep from the results JSON
        # and build a CSV file from it as a BytesIO object
        fields = ["examples", "ground_truth", request.output_field]
        bin_data = self._results_to_binary_file(results, fields)
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
            generated_by=results["model"],
        )

        loguru.logger.info(
            f"Dataset '{dataset_filename}' with ID '{dataset_record.id}' added to the database."
        )

    async def on_job_complete(self, job_id: UUID, task: Callable = None, *args):
        """Watches a submitted job and, when it terminates successfully, runs a given task.

        Inputs:
        - job_id: the UUID of the job to watch
        - task: the function to be called after the job completes successfully
        - args: the arguments to be passed to the function `task()`
        """
        job_status = self.ray_client.get_job_status(job_id)

        valid_status = [
            JobStatus.CREATED.value.lower(),
            JobStatus.PENDING.value.lower(),
            JobStatus.RUNNING.value.lower(),
        ]
        stop_status = [JobStatus.FAILED.value.lower(), JobStatus.SUCCEEDED.value.lower()]

        loguru.logger.info(f"Watching {job_id}")
        while job_status.lower() not in stop_status and job_status.lower() in valid_status:
            await asyncio.sleep(5)
            job_status = self.ray_client.get_job_status(job_id)

        if job_status.lower() == JobStatus.FAILED.value.lower():
            loguru.logger.error(f"Job {job_id} failed: not running task {str(task)}")

        if job_status.lower() == JobStatus.SUCCEEDED.value.lower():
            loguru.logger.info(f"Job {job_id} finished successfully.")
            if task is not None:
                task(*args)

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
        else:
            loguru.logger.info(f"Validation for job type {job_type} not yet supported.")

    def _get_job_params(self, job_type: str, record, request: BaseModel) -> dict:
        # get dataset S3 path from UUID
        dataset_s3_path = self._dataset_service.get_dataset_s3_path(request.dataset)

        # provide a reasonable system prompt for services where none was specified
        if job_type == JobType.EVALUATION or job_type == JobType.INFERENCE:
            if request.system_prompt is None and not request.model.startswith("hf://"):
                request.system_prompt = settings.DEFAULT_SUMMARIZER_PROMPT

        # this section differs between inference and eval
        if job_type == JobType.EVALUATION:
            job_params = {
                "job_id": record.id,
                "job_name": request.name,
                "model_uri": request.model,
                "dataset_path": dataset_s3_path,
                "max_samples": request.max_samples,
                "storage_path": self.storage_path,
                "model_url": self._set_model_type(request),
                "system_prompt": request.system_prompt,
                "skip_inference": request.skip_inference,
            }

        elif job_type == JobType.EVALUATION_LITE:
            job_params = {
                "job_id": record.id,
                "job_name": request.name,
                "model_uri": request.model,
                "dataset_path": dataset_s3_path,
                "max_samples": request.max_samples,
                "storage_path": self.storage_path,
            }
        elif job_type == JobType.INFERENCE:
            job_params = {
                "job_id": record.id,
                "job_name": request.name,
                "model_uri": request.model,
                "dataset_path": dataset_s3_path,
                "task": request.task,
                "accelerator": request.accelerator,
                "revision": request.revision,
                "use_fast": request.use_fast,
                "trust_remote_code": request.trust_remote_code,
                "torch_dtype": request.torch_dtype,
                "max_samples": request.max_samples,
                "storage_path": self.storage_path,
                "model_url": self._set_model_type(request),
                "system_prompt": request.system_prompt,
                "output_field": request.output_field or "predictions",
                "max_tokens": request.max_tokens,
                "frequency_penalty": request.frequency_penalty,
                "temperature": request.temperature,
                "top_p": request.top_p,
            }
        else:
            raise ValueError(f"Job type {job_type} not recognized.")

        return job_params

    def create_job(
        self,
        request: JobCreate,
        background_tasks: BackgroundTasks,
        experiment_id: UUID = None,
    ) -> JobResponse:
        """Creates a new evaluation workload to run on Ray and returns the response status."""
        if request.job_type not in JobType:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Job type not implemented.")
        job_type = request.job_type
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
        # FIXME The ray status is now _not enough_ to set the job status,
        # since the dataset may still be under creation

        loguru.logger.info("Getting response...")
        return JobResponse.model_validate(record)

    def get_job(self, job_id: UUID) -> JobResponse:
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
        record = self._update_job_record(job_id, status=status)
        return JobResponse.model_validate(record)

    def get_job_result(self, job_id: UUID) -> JobResultResponse:
        """Return job results metadata if available in the DB."""
        job_record = self._get_job_record(job_id)
        result_record = self.result_repo.get_by_job_id(job_id)
        if result_record is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                (
                    f"No result available for job '{job_record.name}' "
                    f"(status = '{job_record.status}')."
                ),
            )
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
