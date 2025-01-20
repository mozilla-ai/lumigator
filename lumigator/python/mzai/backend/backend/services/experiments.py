import json
from uuid import UUID

import loguru
from fastapi import BackgroundTasks
from lumigator_schemas.experiments import (
    ExperimentCreate,
    ExperimentResponse,
    ExperimentResultDownloadResponse,
)
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    JobEvalLiteCreate,
    JobInferenceCreate,
    JobStatus,
)
from s3fs import S3FileSystem

from backend.records.jobs import JobRecord
from backend.repositories.experiments import ExperimentRepository
from backend.repositories.jobs import JobRepository
from backend.services.datasets import DatasetService
from backend.services.exceptions.experiment_exceptions import ExperimentNotFoundError
from backend.services.jobs import JobService
from backend.settings import settings


class ExperimentService:
    def __init__(
        self,
        experiment_repo: ExperimentRepository,
        job_repo: JobRepository,
        job_service: JobService,
        dataset_service: DatasetService,
    ):
        self._experiment_repo = experiment_repo
        self._job_repo = job_repo
        self._job_service = job_service
        self._dataset_service = dataset_service

    def _get_all_owned_jobs(self, experiment_id: UUID) -> list[JobRecord]:
        return self._job_repo.get_by_experiment_id(experiment_id)

    def get_all_owned_jobs(self, experiment_id: UUID) -> ListingResponse[UUID]:
        jobs = [job.id for job in self._get_all_owned_jobs(experiment_id)]
        return ListingResponse[UUID].model_validate({"total": len(jobs), "items": jobs})

    def _run_eval(
        self,
        inference_job_id: UUID,
        request: ExperimentCreate,
        background_tasks: BackgroundTasks,
        experiment_id: UUID = None,
    ):
        # use the inference job id to recover the dataset record
        dataset_record = self._dataset_service.get_dataset_by_job_id(inference_job_id)

        # prepare the inputs for the evaluation job and pass the id of the new dataset
        job_eval_dict = {
            "name": f"{request.name}-evaluation",
            "model": request.model,
            "dataset": dataset_record.id,
            "max_samples": request.max_samples,
            "skip_inference": True,
        }

        # submit the job
        self._job_service.create_job(
            JobEvalLiteCreate.model_validate(job_eval_dict),
            background_tasks,
            experiment_id=experiment_id,
        )

    def create_experiment(
        self, request: ExperimentCreate, background_tasks: BackgroundTasks
    ) -> ExperimentResponse:
        # The FastAPI BackgroundTasks object is used to run a function in the background.
        # It is a wrapper around Starlette's BackgroundTasks object.
        # A background task should be attached to a response,
        # and will run only once the response has been sent.
        # See here: https://www.starlette.io/background/

        experiment_record = self._experiment_repo.create(
            name=request.name, description=request.description
        )
        loguru.logger.info(f"Created experiment '{request.name}' with ID '{experiment_record.id}'.")

        # input is ExperimentCreate, we need to split the configs and generate one
        # JobInferenceCreate and one JobEvalCreate
        job_inference_dict = {
            "name": f"{request.name}-inference",
            "model": request.model,
            "dataset": request.dataset,
            "max_samples": request.max_samples,
            "model_url": request.model_url,
            "output_field": request.inference_output_field,
            "system_prompt": request.system_prompt,
            "store_to_dataset": True,
        }

        # submit inference job first
        job_response = self._job_service.create_job(
            JobInferenceCreate.model_validate(job_inference_dict),
            background_tasks,
            experiment_id=experiment_record.id,
        )

        # run evaluation job afterwards
        # (NOTE: tasks in starlette are executed sequentially: https://www.starlette.io/background/)
        background_tasks.add_task(
            self._job_service.on_job_complete,
            job_response.id,
            self._run_eval,
            job_response.id,
            request,
            background_tasks,
            experiment_record.id,
        )

        return ExperimentResponse.model_validate(experiment_record)

    # TODO Move this into a "composite job" impl
    def get_experiment(self, experiment_id: UUID) -> ExperimentResponse:
        """Gets an experiment by ID.

        :param experiment_id: the ID of the experiment to return information for
        :returns: information on the experiment, such as the ID, name, status etc.
        :rtype: ExperimentResponse
        :raises ExperimentNotFoundError: if the experiment does not exist
        """
        record = self._experiment_repo.get(experiment_id)
        if record is None:
            raise ExperimentNotFoundError(experiment_id) from None

        loguru.logger.info(f"Obtaining info for experiment {experiment_id}: {record}")

        all_succeeded = True
        for job in self._get_all_owned_jobs(experiment_id):
            loguru.logger.info(f"Checking sub job: {job}")
            if self._job_service.get_job(job.id).status != JobStatus.SUCCEEDED:
                all_succeeded = False
                break

        if all_succeeded:
            record = self._experiment_repo.update(experiment_id, status=JobStatus.SUCCEEDED)

        return ExperimentResponse.model_validate(record)

    def _get_experiment_jobs(self, experiment_id: UUID):
        records = self._job_repo.get_by_experiment_id(experiment_id)
        return records

    def get_experiment_result_download(
        self, experiment_id: UUID
    ) -> ExperimentResultDownloadResponse:
        """Return experiment results file URL for downloading."""
        s3 = S3FileSystem()
        # get jobs matching this experiment
        # have a query returning a list of (two) jobs, one inference and one eval,
        # matching the current experiment id. Note that each job has its own type baked in
        # (per https://github.com/mozilla-ai/lumigator/pull/576)
        jobs = self._get_experiment_jobs(experiment_id)

        # iterate on jobs and depending on which job this is, import selected fields
        results = {}

        for job in jobs:
            # Get the dataset from the S3 bucket
            result_key = self._job_service._get_results_s3_key(job.id)
            with s3.open(f"{settings.S3_BUCKET}/{result_key}", "r") as f:
                job_results = json.loads(f.read())

            # we just merge the two dictionaries for now
            results.update(job_results)

        loguru.logger.error(results)

        # Generate presigned download URL for the object
        result_key = self._job_service._get_results_s3_key(experiment_id)
        download_url = self._dataset_service.s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": result_key,
            },
            ExpiresIn=settings.S3_URL_EXPIRATION,
        )

        return ExperimentResultDownloadResponse(id=experiment_id, download_url=download_url)

    def list_experiments(
        self, skip: int = 0, limit: int = 100
    ) -> ListingResponse[ExperimentResponse]:
        records = self._experiment_repo.list(skip, limit)
        return ListingResponse(
            total=self._experiment_repo.count(),
            items=[ExperimentResponse.model_validate(x) for x in records],
        )
