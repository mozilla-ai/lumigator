from pathlib import Path
from uuid import UUID

from mzai.backend.schemas.experiments import (
    ExperimentCreate,
    ExperimentResponse,
    ExperimentResultDownloadResponse,
    ExperimentResultResponse,
)
from mzai.backend.schemas.extras import ListingResponse

from sdk.client import ApiClient


class Experiments:
    EXPERIMENTS_ROUTE = "experiments"

    def __init__(self, c: ApiClient):
        self.client = c

    def create_experiment(self, experiment: ExperimentCreate) -> ExperimentResponse:
        """Creates a new experiment."""
        response = self.__post_response(str(Path(self.client._api_url) / self.EXPERIMENTS_ROUTE / ''), experiment.model_dump_json())

        if not response:
            return []

        data = response.json()
        return ExperimentResponse(**data)

    def get_experiment(self, experiment_id: UUID) -> ExperimentResponse:
        """Returns information on the experiment for the specified ID."""
        response = self.__get_response(str(Path(self._api_url) / self.EXPERIMENTS_ROUTE))

        if not response:
            return []

        data = response.json()
        return ExperimentResponse(**data)

    def get_experiments(self, skip: int = 0, limit: int = 100) -> ListingResponse[ExperimentResponse]:
        """Returns information on all experiments."""
        response = self.__get_response(str(Path(self._api_url) / self.EXPERIMENTS_ROUTE))

        if not response:
            return []

        return [ExperimentResponse(**args) for args in response.json()]

    def get_experiment_result(self, experiment_id: UUID) -> ExperimentResultResponse:
        """Returns the result of the experiment for the specified ID."""
        response = self.client.__get_response(str(Path(self._api_url) / self.EXPERIMENTS_ROUTE / f'{experiment_id}' / "result"))

        if not response:
            return []

        data = response.json()
        return ExperimentResultResponse(**data)

    def get_experiment_result_download(self, experiment_id: UUID) -> ExperimentResultDownloadResponse:
        """Returns the result of the experiment for the specified ID."""
        response = self.__get_response(
            str(Path(self.client._api_url) / self.EXPERIMENTS_ROUTE / f'{experiment_id}' / "result" / "download"))

        if not response:
            return []

        data = response.json()
        return ExperimentResultDownloadResponse(**data)