from http import HTTPMethod, HTTPStatus
from json import dumps
from uuid import UUID

from lumigator_schemas.experiments import (
    ExperimentCreate,
    ExperimentResponse,
    ExperimentResultDownloadResponse,
    ExperimentResultResponse,
)
from lumigator_schemas.extras import ListingResponse

from lumigator_sdk.client import ApiClient
from lumigator_sdk.strict_schemas import ExperimentCreate as ExperimentCreateStrict


class Experiments:
    EXPERIMENTS_ROUTE = "experiments"

    def __init__(self, c: ApiClient):
        self.__client = c

    def create_experiment(self, experiment: ExperimentCreate) -> ExperimentResponse:
        """Creates a new experiment."""
        ExperimentCreateStrict.model_validate(ExperimentCreate.model_dump(experiment))
        response = self.__client.get_response(
            self.EXPERIMENTS_ROUTE, HTTPMethod.POST, dumps(experiment)
        )

        if not response:
            return []

        data = response.json()
        return ExperimentResponse(**data)

    def get_experiment(self, experiment_id: UUID) -> ExperimentResponse | None:
        """Returns information on the experiment for the specified ID."""
        response = self.__client.get_response(f"{self.EXPERIMENTS_ROUTE}/{experiment_id}")

        if not response or response.status_code != HTTPStatus.OK:
            return None

        data = response.json()
        return ExperimentResponse(**data)

    def get_experiments(
        self, skip: int = 0, limit: int = 100
    ) -> ListingResponse[ExperimentResponse]:
        """Returns information on all experiments."""
        response = self.__client.get_response(self.EXPERIMENTS_ROUTE)

        if not response:
            return []

        return [ExperimentResponse(**args) for args in response.json()]

    def get_experiment_result(self, experiment_id: UUID) -> ExperimentResultResponse | None:
        """Returns the result of the experiment for the specified ID."""
        response = self.__client.get_response(f"{self.EXPERIMENTS_ROUTE}/{experiment_id}/result")

        if not response or response.status_code != HTTPStatus.OK:
            return None

        data = response.json()
        return ExperimentResultResponse(**data)

    def get_experiment_result_download(
        self, experiment_id: UUID
    ) -> ExperimentResultDownloadResponse | None:
        """Returns the result of the experiment for the specified ID."""
        response = self.__client.get_response(
            f"{self.EXPERIMENTS_ROUTE}/{experiment_id}/result/download"
        )

        if not response or response.status_code != HTTPStatus.OK:
            return None

        data = response.json()
        return ExperimentResultDownloadResponse(**data)
