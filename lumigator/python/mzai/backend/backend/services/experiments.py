from uuid import UUID

import loguru
from fastapi import HTTPException, status
from lumigator_schemas.experiments import ExperimentIdCreate, ExperimentResponse

from backend.records.experiments import ExperimentRecord
from backend.repositories.experiments import ExperimentRepository
from backend.repositories.jobs import JobRepository
from backend.services.datasets import DatasetService
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

    def _raise_not_found(self, job_id: UUID):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Job {job_id} not found.")

    def _get_experiment_record(self, experiment_id: UUID) -> ExperimentRecord:
        record = self._experiment_repo.get(experiment_id)
        if record is None:
            self._raise_not_found(experiment_id)
        return record

    def create_experiment(self, request: ExperimentIdCreate) -> ExperimentResponse:
        experiment_record = self._experiment_repo.create(
            name=request.name, description=request.description
        )
        loguru.logger.info(f"Created experiment '{request.name}' with ID '{experiment_record.id}'.")

        return ExperimentResponse.model_validate(experiment_record)
