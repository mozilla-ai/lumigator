from pathlib import Path
from uuid import UUID
from http import HTTPMethod
from json import dumps

from schemas.experiments import (
    ExperimentCreate,
    ExperimentResponse,
    ExperimentResultDownloadResponse,
    ExperimentResultResponse,
)
from schemas.extras import ListingResponse

from client import ApiClient


class Experiments:
    EXPERIMENTS_ROUTE = "experiments"

    def __init__(self, c: ApiClient):
        self.client = c

    def create_experiment(self, experiment: ExperimentCreate) -> ExperimentResponse:
        """Creates a new experiment."""
        response = self.client.get_response(str(Path(self.client._api_url) / self.EXPERIMENTS_ROUTE / ''), HTTPMethod.POST, dumps(experiment))

        if not response:
            return []

        data = response.json()
        return ExperimentResponse(**data)

    def get_experiment(self, experiment_id: UUID) -> ExperimentResponse:
        """Returns information on the experiment for the specified ID."""
        response = self.client.get_response(self.EXPERIMENTS_ROUTE)

        if not response:
            return []

        data = response.json()
        return ExperimentResponse(**data)

    def get_experiments(self, skip: int = 0, limit: int = 100) -> ListingResponse[ExperimentResponse]:
        """Returns information on all experiments."""
        response = self.client.get_response(self.EXPERIMENTS_ROUTE)

        if not response:
            return []

        return [ExperimentResponse(**args) for args in response.json()]

    def get_experiment_result(self, experiment_id: UUID) -> ExperimentResultResponse:
        """Returns the result of the experiment for the specified ID."""
        response = self.client.get_response(f'{self.EXPERIMENTS_ROUTE}/{experiment_id}/result')

        if not response:
            return []

        data = response.json()
        return ExperimentResultResponse(**data)

    def get_experiment_result_download(self, experiment_id: UUID) -> ExperimentResultDownloadResponse:
        """Returns the result of the experiment for the specified ID."""
        response = self.client.get_response(f'{self.EXPERIMENTS_ROUTE}/{experiment_id}/result/download')

        if not response:
            return []

        data = response.json()
        return ExperimentResultDownloadResponse(**data)