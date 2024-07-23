import os
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, status
from ray.job_submission import JobSubmissionClient

from mzai.backend.jobs.submission import RayJobEntrypoint, submit_ray_job
from mzai.backend.records.experiments import ExperimentRecord
from mzai.backend.repositories.experiments import ExperimentRepository, ExperimentResultRepository
from mzai.backend.services.datasets import DatasetService
from mzai.backend.settings import settings
from mzai.schemas.experiments import (
    ExperimentCreate,
    ExperimentResponse,
    ExperimentResultDownloadResponse,
    ExperimentResultResponse,
)
from mzai.schemas.extras import ListingResponse
from mzai.schemas.jobs import JobConfig, JobStatus, JobType


class ExperimentService:
    def __init__(
        self,
        experiment_repo: ExperimentRepository,
        result_repo: ExperimentResultRepository,
        ray_client: JobSubmissionClient,
        data_service: DatasetService,
    ):
        self.experiment_repo = experiment_repo
        self.result_repo = result_repo
        self.ray_client = ray_client
        self.data_service = data_service

    def _raise_not_found(self, experiment_id: UUID):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Experiment {experiment_id} not found.")

    def _get_experiment_record(self, experiment_id: UUID) -> ExperimentRecord:
        record = self.experiment_repo.get(experiment_id)
        if record is None:
            self._raise_not_found(experiment_id)
        return record

    def _update_experiment_record(self, job_id: UUID, **updates) -> ExperimentRecord:
        record = self.experiment_repo.update(job_id, **updates)
        if record is None:
            self._raise_not_found(job_id)
        return record

    def _get_results_s3_key(self, experiment_id: UUID) -> str:
        """Given an experiment ID, returns the S3 key for the experiment results.

        The S3 key is built from:
        - settings.S3_EXPERIMENT_RESULTS_PREFIX: the path where experiments are stored
        - settings.S3_EXPERIMENT_RESULTS_FILENAME: a filename template that is to be
          formatted with some of the experiment record's metadata (e.g. exp name/id)

        The returned string contains the S3 key *excluding the bucket / s3 prefix*,
        as it is to be used by the boto3 client which accepts them separately.
        """
        record = self._get_experiment_record(experiment_id)

        return str(
            Path(settings.S3_EXPERIMENT_RESULTS_PREFIX)
            / settings.S3_EXPERIMENT_RESULTS_FILENAME.format(
                experiment_name=record.name, experiment_id=record.id
            )
        )

    def create_experiment(self, request: ExperimentCreate) -> ExperimentResponse:
        record = self.experiment_repo.create(name=request.name, description=request.description)

        # get dataset S3 path from UUID
        dataset_s3_path = self.data_service.get_dataset_s3_path(request.dataset)

        # set storage path
        storage_path = f"s3://{ Path(settings.S3_BUCKET) / settings.S3_EXPERIMENT_RESULTS_PREFIX }/"

        eval_config_dict = {
            "name": f"{request.name}/{str(record.id)}",
            "model": {"path": request.model},
            "dataset": {"path": dataset_s3_path},
            "evaluation": {
                "metrics": ["rouge", "meteor", "bertscore"],
                "use_pipeline": True,
                "max_samples": request.max_samples,
                "return_input_data": True,
                "return_predictions": True,
                "storage_path": storage_path,
            },
        }

        # Submit the job to Ray
        ray_config = JobConfig(
            job_id=record.id,
            job_type=JobType.EXPERIMENT,
            args=eval_config_dict,
        )

        runtime_env = {
            "pip": ["lm-buddy==0.10.10"],
            "env_vars": {
                "MZAI_JOB_ID": str(record.id),
                "MZAI_HOST": "",
                "LOCAL_FSSPEC_S3_KEY": os.environ.get("LOCAL_FSSPEC_S3_KEY", ""),
                "LOCAL_FSSPEC_S3_SECRET": os.environ.get("LOCAL_FSSPEC_S3_SECRET", ""),
                "LOCAL_FSSPEC_S3_ENDPOINT_URL": os.environ.get("LOCAL_FSSPEC_S3_ENDPOINT_URL", ""),
            },
        }
        entrypoint = RayJobEntrypoint(config=ray_config, runtime_env=runtime_env)
        submit_ray_job(self.ray_client, entrypoint)

        return ExperimentResponse.model_validate(record)

    def get_experiment(self, experiment_id: UUID) -> ExperimentResponse:
        record = self._get_experiment_record(experiment_id)
        return ExperimentResponse.model_validate(record)

    def list_experiments(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> ListingResponse[ExperimentResponse]:
        total = self.experiment_repo.count()
        records = self.experiment_repo.list(skip, limit)
        return ListingResponse(
            total=total,
            items=[ExperimentResponse.model_validate(x) for x in records],
        )

    def update_experiment_status(
        self,
        experiment_id: UUID,
        status: JobStatus,
    ) -> ExperimentResponse:
        record = self._update_experiment_record(experiment_id, status=status)
        return ExperimentResponse.model_validate(record)

    def get_experiment_result(self, experiment_id: UUID) -> ExperimentResultResponse:
        """Return experiment results metadata if available in the DB."""
        experiment_record = self._get_experiment_record(experiment_id)
        result_record = self.result_repo.get_by_experiment_id(experiment_id)
        if result_record is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                (
                    f"No result available for experiment '{experiment_record.name}' "
                    f"(status = '{experiment_record.status}')."
                ),
            )
        return ExperimentResultResponse.model_validate(result_record)

    def get_experiment_result_download(
        self, experiment_id: UUID
    ) -> ExperimentResultDownloadResponse:
        """Return experiment results file URL for downloading."""
        # Generate presigned download URL for the object
        result_key = self._get_results_s3_key(experiment_id)
        download_url = self.data_service.s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": result_key,
            },
            ExpiresIn=settings.S3_URL_EXPIRATION,
        )

        return ExperimentResultDownloadResponse(id=experiment_id, download_url=download_url)
