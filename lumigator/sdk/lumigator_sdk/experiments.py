from http import HTTPMethod
from json import dumps

from lumigator_schemas.experiments import (
    ExperimentIdCreate,
    ExperimentIdResponse,
    ExperimentResponse,
    GetExperimentResponse,
)
from lumigator_schemas.extras import ListingResponse

from lumigator_sdk.client import ApiClient
from lumigator_sdk.strict_schemas import ExperimentIdCreate as ExperimentIdCreateStrict


class Experiments:
    EXPERIMENTS_ROUTE = "experiments/new"

    def __init__(self, c: ApiClient):
        self.__client = c

    def create_experiment(self, experiment: ExperimentIdCreate) -> ExperimentIdResponse:
        """Creates a new experiment."""
        ExperimentIdCreateStrict.model_validate(ExperimentIdCreate.model_dump(experiment))
        response = self.__client.get_response(
            self.EXPERIMENTS_ROUTE, HTTPMethod.POST, dumps(experiment)
        )

        data = response.json()
        return ExperimentResponse(**data)

    def get_experiment(self, experiment_id: str) -> GetExperimentResponse | None:
        """Returns information on the experiment for the specified ID."""
        response = self.__client.get_response(f"{self.EXPERIMENTS_ROUTE}/{experiment_id}")

        data = response.json()
        return GetExperimentResponse(**data)

    def get_experiments(
        self, skip: int = 0, limit: int = 100
    ) -> ListingResponse[ExperimentResponse]:
        """Returns information on all experiments."""
        response = self.__client.get_response(f"{self.EXPERIMENTS_ROUTE}/all")

        data = response.json()
        return ListingResponse[ExperimentResponse](**data)

    def delete_experiment(self, experiment_id: str) -> None:
        """Deletes the experiment for the specified ID."""
        self.__client.get_response(f"{self.EXPERIMENTS_ROUTE}/{experiment_id}", HTTPMethod.DELETE)
        return None
