import loguru
from lumigator_schemas.experiments import (
    ExperimentCreate,
    GetExperimentResponse,
)
from lumigator_schemas.extras import ListingResponse

from backend.repositories.jobs import JobRepository
from backend.services.datasets import DatasetService
from backend.services.exceptions.experiment_exceptions import ExperimentNotFoundError
from backend.services.jobs import JobService
from backend.tracking import TrackingClient


class ExperimentService:
    def __init__(
        self,
        job_repo: JobRepository,
        job_service: JobService,
        dataset_service: DatasetService,
        tracking_session: TrackingClient,
    ):
        self._job_repo = job_repo
        self._job_service = job_service
        self._dataset_service = dataset_service
        self._tracking_session = tracking_session

    async def create_experiment(self, request: ExperimentCreate) -> GetExperimentResponse:
        experiment = await self._tracking_session.create_experiment(
            request.name,
            request.description,
            request.task_definition,
            request.dataset,
            request.max_samples,
        )
        loguru.logger.info(f"Created tracking experiment '{experiment.name}' with ID '{experiment.id}'.")
        return experiment

    async def get_experiment(self, experiment_id: str) -> GetExperimentResponse:
        record = await self._tracking_session.get_experiment(experiment_id)
        if record is None:
            raise ExperimentNotFoundError(experiment_id) from None
        return GetExperimentResponse.model_validate(record)

    async def list_experiments(self, skip: int, limit: int) -> ListingResponse[GetExperimentResponse]:
        records = await self._tracking_session.list_experiments(skip, limit)
        total = await self._tracking_session.experiments_count()
        return ListingResponse(
            total=total,
            items=[GetExperimentResponse.model_validate(x) for x in records],
        )

    async def delete_experiment(self, experiment_id: str):
        await self._tracking_session.delete_experiment(experiment_id)
