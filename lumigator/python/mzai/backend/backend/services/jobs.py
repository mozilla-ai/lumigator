from pathlib import Path
from uuid import UUID

import loguru
from fastapi import HTTPException, status
from ray.job_submission import JobSubmissionClient
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    JobConfig,
    JobCreate,
    JobResponse,
    JobResultDownloadResponse,
    JobResultResponse,
    JobStatus,
    JobType,
)

from backend import config_templates
from backend.ray_submit.submission import RayJobEntrypoint, submit_ray_job
from backend.records.jobs import JobRecord
from backend.repositories.jobs import JobRepository, JobResultRepository
from backend.services.datasets import DatasetService
from backend.settings import settings


class JobService:
    def __init__(
        self,
        job_repo: JobRepository,
        result_repo: JobResultRepository,
        ray_client: JobSubmissionClient,
        data_service: DatasetService,
    ):
        self.job_repo = job_repo
        self.result_repo = result_repo
        self.ray_client = ray_client
        self.data_service = data_service

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
            / settings.S3_JOB_RESULTS_FILENAME.format(
                job_name=record.name, job_id=record.id
            )
        )

    def create_inference_job(self, request: JobCreate) -> JobResponse:
        """Creates a new workload to perform batch inference"""
        # Create a db record for the job
        record = self.job_repo.create(name=request.name, description=request.description)

        # get dataset S3 path from UUID
        dataset_s3_path = self.data_service.get_dataset_s3_path(request.dataset)

        # set storage path
        storage_path = f"s3://{Path(settings.S3_BUCKET) / settings.S3_JOB_RESULTS_PREFIX}/"

        # fill up model url with default openai url
        if request.model.startswith("oai://"):
            model_url = settings.OAI_API_URL
        elif request.model.startswith("mistral://"):
            model_url = settings.MISTRAL_API_URL
        else:
            model_url = request.model_url

        # provide a reasonable system prompt for services where none was specified
        if request.system_prompt is None and not request.model.startswith("hf://"):
            request.system_prompt = settings.DEFAULT_SUMMARIZER_PROMPT

        config_params = {
            "job_name": request.name,
            "job_id": record.id,
            "model_path": request.model,
            "dataset_path": dataset_s3_path,
            "max_samples": request.max_samples,
            "storage_path": storage_path,
            "model_url": model_url,
            "system_prompt": request.system_prompt,
        }


        # load a config template and fill it up with config_params
        if request.config_infer_template is not None:
            config_template = request.config_infer_template
        elif request.model in config_templates.config_infer_template:
            # if no config template is provided, get the default one for the model
            config_template = config_templates.config_infer_template[request.model]
        else:
            # if no default config template is provided, get the causal template
            # (which works with seq2seq models too except it does not use pipeline)
            config_template = config_templates.causal_infer_template

        infer_config_args = {
            "--config": config_template.format(**config_params),
        }

        #TODO Add inference module as entrypoint
        infer_command = f"{settings.LD_PRELOAD_PREFIX} python -m inference infer huggingface"

        # Prepare the job configuration that will be sent to submit the ray job.
        # This includes both the command that is going to be executed and its
        # arguments defined in infer_config_args
        ray_config = JobConfig(
            job_id=record.id,
            job_type=JobType.INFERENCE,
            command=infer_command,
            args=infer_config_args,
        )

        # build runtime ENV for workers
        runtime_env_vars = {"MZAI_JOB_ID": str(record.id)}
        settings.inherit_ray_env(runtime_env_vars)

        # set num_gpus per worker (zero if we are just hitting a service)
        if not request.model.startswith("hf://"):
            worker_gpus = settings.RAY_WORKER_GPUS_FRACTION
        else:
            worker_gpus = settings.RAY_WORKER_GPUS

        runtime_env = {
            "pip": settings.PIP_REQS,
            "working_dir": settings.EVALUATOR_WORK_DIR,
            "env_vars": runtime_env_vars,
        }

        loguru.logger.info("runtime env setup...")
        loguru.logger.info(f"{runtime_env}")

        entrypoint = RayJobEntrypoint(
            config=ray_config, runtime_env=runtime_env, num_gpus=worker_gpus
        )
        loguru.logger.info("Submitting Ray job...")
        submit_ray_job(self.ray_client, entrypoint)

        loguru.logger.info("Getting response...")
        return JobResponse.model_validate(record)

    def create_evaluation_job(self, request: JobCreate) -> JobResponse:
        """Creates a new evaluation workload to run on Ray and returns the response status"""
        # Create a db record for the job
        record = self.job_repo.create(name=request.name, description=request.description)

        # get dataset S3 path from UUID
        dataset_s3_path = self.data_service.get_dataset_s3_path(request.dataset)

        # set storage path
        storage_path = f"s3://{ Path(settings.S3_BUCKET) / settings.S3_JOB_RESULTS_PREFIX }/"

        # fill up model url with default openai url
        if request.model.startswith("oai://"):
            model_url = settings.OAI_API_URL
        elif request.model.startswith("mistral://"):
            model_url = settings.MISTRAL_API_URL
        else:
            model_url = request.model_url

        # provide a reasonable system prompt for services where none was specified
        if request.system_prompt is None and not request.model.startswith("hf://"):
            request.system_prompt = settings.DEFAULT_SUMMARIZER_PROMPT

        config_params = {
            "job_name": request.name,
            "job_id": record.id,
            "model_path": request.model,
            "dataset_path": dataset_s3_path,
            "max_samples": request.max_samples,
            "storage_path": storage_path,
            "model_url": model_url,
            "system_prompt": request.system_prompt,
        }

        # load a config template and fill it up with config_params
        if request.config_eval_template is not None:
            config_template = request.config_eval_template
        elif request.model in config_templates.config_eval_template:
            # if no config template is provided, get the default one for the model
            config_template = config_templates.config_eval_template[request.model]
        else:
            # if no default config template is provided, get the causal template
            # (which works with seq2seq models too except it does not use pipeline)
            config_template = config_templates.causal_eval_template

        # eval_config_args is used to map input configuration parameters with
        # command parameters provided via command line to the ray job.
        # To do this, we use a dict where keys are parameter names as they'd
        # appear on the command line and the values are the respective params.
        eval_config_args = {
            "--config": config_template.format(**config_params),
        }

        # Pre-loading libgomp with LD_PRELOAD resolves allocation issues on aarch64
        # (see https://github.com/mozilla-ai/lumigator/issues/156). The path where
        # libs are stored on worker nodes contains a hash that depends on the
        # installed libraries, so we get it dynamically right before running the
        # command (more info in settings.py)
        eval_command = f"{settings.LD_PRELOAD_PREFIX} python -m evaluator evaluate huggingface"

        # Prepare the job configuration that will be sent to submit the ray job.
        # This includes both the command that is going to be executed and its
        # arguments defined in eval_config_args
        ray_config = JobConfig(
            job_id=record.id,
            job_type=JobType.EVALUATION,
            command=eval_command,
            args=eval_config_args,
        )

        # build runtime ENV for workers
        runtime_env_vars = {"MZAI_JOB_ID": str(record.id)}
        settings.inherit_ray_env(runtime_env_vars)

        # set num_gpus per worker (zero if we are just hitting a service)
        if not request.model.startswith("hf://"):
            worker_gpus = settings.RAY_WORKER_GPUS_FRACTION
        else:
            worker_gpus = settings.RAY_WORKER_GPUS

        runtime_env = {
            "pip": settings.PIP_REQS,
            "working_dir": settings.EVALUATOR_WORK_DIR,
            "env_vars": runtime_env_vars,
        }

        loguru.logger.info("runtime env setup...")
        loguru.logger.info(f"{runtime_env}")

        entrypoint = RayJobEntrypoint(
            config=ray_config, runtime_env=runtime_env, num_gpus=worker_gpus
        )
        loguru.logger.info("Submitting Ray job...")
        submit_ray_job(self.ray_client, entrypoint)

        loguru.logger.info("Getting response...")
        return JobResponse.model_validate(record)

    def get_job(self, job_id: UUID) -> JobResponse:
        record = self._get_job_record(job_id)
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
            items=[JobResponse.model_validate(x) for x in records],
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

    def get_job_result_download(
        self, job_id: UUID
    ) -> JobResultDownloadResponse:
        """Return job results file URL for downloading."""
        # Generate presigned download URL for the object
        result_key = self._get_results_s3_key(job_id)
        download_url = self.data_service.s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": result_key,
            },
            ExpiresIn=settings.S3_URL_EXPIRATION,
        )

        return JobResultDownloadResponse(id=job_id, download_url=download_url)
