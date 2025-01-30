from uuid import UUID

import loguru
from lumigator_schemas.experiments import (
    ExperimentCreate,
    ExperimentResponse,
)
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    JobStatus,
)

from backend.records.jobs import JobRecord
from backend.repositories.experiments import ExperimentRepository
from backend.repositories.jobs import JobRepository
from backend.services.datasets import DatasetService
from backend.services.exceptions.experiment_exceptions import ExperimentNotFoundError
from backend.services.jobs import JobService


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

    def create_experiment(self, request: ExperimentCreate) -> ExperimentResponse:
        experiment_record = self._experiment_repo.create(
            name=request.name, description=request.description
        )
        loguru.logger.info(f"Created experiment '{request.name}' with ID '{experiment_record.id}'.")

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
        any_running = False
        any_failed = False
        # Any running: running
        # Any failed: failed
        # All succeeded: succeeded
        for job in self._get_all_owned_jobs(experiment_id):
            loguru.logger.info(f"Checking sub job: {job}")
            if self._job_service.get_job(job.id).status != JobStatus.SUCCEEDED:
                all_succeeded = False
                if self._job_service.get_job(job.id).status == JobStatus.FAILED:
                    any_failed = True
                    # Any failed job makes further inspection unnecessary
                    break
                if self._job_service.get_job(job.id).status == JobStatus.RUNNING:
                    any_running = True
                    # Any running job will move status to running, but
                    # searching for failures is still necessary

        if all_succeeded:
            record = self._experiment_repo.update(experiment_id, status=JobStatus.SUCCEEDED)
        elif any_failed:
            record = self._experiment_repo.update(experiment_id, status=JobStatus.FAILED)
        elif any_running:
            record = self._experiment_repo.update(experiment_id, status=JobStatus.RUNNING)
        else:
            record = self._experiment_repo.update(experiment_id, status=JobStatus.PENDING)

        return ExperimentResponse.model_validate(record)

    def list_experiments(
        self, skip: int = 0, limit: int = 100
    ) -> ListingResponse[ExperimentResponse]:
        records = self._experiment_repo.list(skip, limit)
        return ListingResponse(
            total=self._experiment_repo.count(),
            items=[ExperimentResponse.model_validate(x) for x in records],
        )
