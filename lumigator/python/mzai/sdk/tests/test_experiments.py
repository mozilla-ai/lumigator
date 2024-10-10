from datetime import datetime
from schemas.experiments import ExperimentResponse
from tests.helpers import load_json


def test_get_experiments_ok(
    mock_requests_response, mock_requests, lumi_client, json_data_experiments
):
    mock_requests_response.status_code = 200
    data = load_json(json_data_experiments)
    mock_requests_response.json = lambda: data

    experiments_ret = lumi_client.experiments.get_experiments()
    assert experiments_ret is not None
    assert len(experiments_ret) == 2
    assert any(
        str(x.id) == "daab39ac-be9f-4de9-87c0-c4c94b297a97" and x.name == "exp1"
        for x in experiments_ret
    )
    assert any(
        str(x.id) == "e3be6e4b-dd1e-43b7-a97b-0d47dcc49a4f" and x.name == "exp2"
        for x in experiments_ret
    )


def test_get_experiment_ok(
    mock_requests_response, mock_requests, lumi_client, json_data_experiment
):
    mock_requests_response.status_code = 200
    data = load_json(json_data_experiment)
    mock_requests_response.json = lambda: data
    experiment_ret = lumi_client.experiments.get_experiment("daab39ac-be9f-4de9-87c0-c4c94b297a97")
    assert experiment_ret is not None
    assert str(experiment_ret.id) == "daab39ac-be9f-4de9-87c0-c4c94b297a97"
    assert experiment_ret.name == "exp1"
    assert experiment_ret.status == "created"


def test_create_experiment_ok_simple(
    mock_requests_response,
    mock_requests,
    lumi_client,
    json_data_experiment_post_response,
    json_data_experiment_post_simple,
):
    mock_requests_response.status_code = 200
    data = load_json(json_data_experiment_post_response)
    mock_requests_response.json = lambda: data

    experiment_json = load_json(json_data_experiment_post_simple)
    experiment_ret = lumi_client.experiments.create_experiment(experiment_json)
    assert experiment_ret is not None
    assert str(experiment_ret.id) == "daab39ac-be9f-4de9-87c0-c4c94b297a97"
    assert experiment_ret.name == "experiment"
    assert experiment_ret.status == "created"


def test_create_experiment_ok_all(
    mock_requests_response,
    mock_requests,
    lumi_client,
    json_data_experiment_post_response,
    json_data_experiment_post_all,
):
    mock_requests_response.status_code = 200
    data = load_json(json_data_experiment_post_response)
    mock_requests_response.json = lambda: data

    experiment_json = load_json(json_data_experiment_post_all)
    experiment_ret = lumi_client.experiments.create_experiment(experiment_json)

    assert experiment_ret is not None
    assert str(experiment_ret.id) == "daab39ac-be9f-4de9-87c0-c4c94b297a97"
    assert experiment_ret.name == "experiment"
    assert experiment_ret.status == "created"
