import loguru
from lumigator_schemas.experiments import (
    ExperimentCreate,
    ExperimentIdResponse,
    ExperimentResponse,
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

    def create_experiment(self, request: ExperimentCreate) -> ExperimentIdResponse:
        experiment = self._tracking_session.create_experiment(request.name, request.description)
        loguru.logger.info(
            f"Created tracking experiment '{experiment.name}' with ID '{experiment.id}'."
        )
        return experiment

    def get_experiment(self, experiment_id: str) -> GetExperimentResponse:
        record = self._tracking_session.get_experiment(experiment_id)
        if record is None:
            raise ExperimentNotFoundError(experiment_id) from None
        return GetExperimentResponse.model_validate(record)

    def list_experiments(self, skip: int, limit: int) -> ListingResponse[ExperimentResponse]:
        records = self._tracking_session.list_experiments(skip, limit)
        return ListingResponse(
            total=self._tracking_session.experiments_count(),
            items=[ExperimentResponse.model_validate(x) for x in records],
        )

    def delete_experiment(self, experiment_id: str):
        self._tracking_session.delete_experiment(experiment_id)
