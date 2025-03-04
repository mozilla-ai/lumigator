from http import HTTPStatus

from lumigator_schemas.experiments import ExperimentCreate
from lumigator_sdk.experiments import Experiments
from tests.helpers import load_json


def test_create_experiment_ok_all(
    lumi_client, json_data_experiment_post_response, json_data_experiment_post_all, request_mock
):
    # Load the experiment data from the parameterized fixture
    experiment_json = load_json(json_data_experiment_post_all)

    # Mock the API endpoint
    request_mock.post(
        url=lumi_client.client._api_url + f"/{Experiments.EXPERIMENTS_ROUTE}",
        status_code=HTTPStatus.OK,
        json=load_json(json_data_experiment_post_response),
    )

    # Create and validate the experiment
    experiment_ret = lumi_client.experiments.create_experiment(ExperimentCreate.model_validate(experiment_json))

    # Assertions
    assert experiment_ret is not None
    assert str(experiment_ret.id) == "daab39ac-be9f-4de9-87c0-c4c94b297a97"
    assert experiment_ret.name == "experiment"
    assert experiment_ret.description == "test experiment"
