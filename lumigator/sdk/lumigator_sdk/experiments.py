from http import HTTPMethod

from lumigator_schemas.experiments import (
    ExperimentCreate,
    GetExperimentResponse,
)
from lumigator_schemas.extras import ListingResponse

from lumigator_sdk.client import ApiClient
from lumigator_sdk.strict_schemas import ExperimentCreate as ExperimentCreateStrict


class Experiments:
    EXPERIMENTS_ROUTE = "experiments"

    def __init__(self, c: ApiClient):
        self.__client = c

    def create_experiment(self, experiment: ExperimentCreate) -> GetExperimentResponse:
        """Creates a new experiment."""
        ExperimentCreateStrict.model_validate(ExperimentCreate.model_dump(experiment))
        response = self.__client.get_response(self.EXPERIMENTS_ROUTE, HTTPMethod.POST, experiment.model_dump_json())

        data = response.json()
        return GetExperimentResponse(**data)

    def get_experiment(self, experiment_id: str) -> GetExperimentResponse | None:
        """Returns information on the experiment for the specified ID."""
        response = self.__client.get_response(f"{self.EXPERIMENTS_ROUTE}/{experiment_id}")

        data = response.json()
        return GetExperimentResponse(**data)

    def get_experiments(self, skip: int = 0, limit: int = 100) -> ListingResponse[GetExperimentResponse]:
        """Returns information on all experiments."""
        response = self.__client.get_response(f"{self.EXPERIMENTS_ROUTE}/all")

        data = response.json()
        return ListingResponse[GetExperimentResponse](**data)

    def delete_experiment(self, experiment_id: str) -> None:
        """Deletes the experiment for the specified ID."""
        self.__client.get_response(f"{self.EXPERIMENTS_ROUTE}/{experiment_id}", HTTPMethod.DELETE)
        return None
