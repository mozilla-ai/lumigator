from tests.helpers import load_json


def test_get_experiments_ok(
    mock_requests_response, mock_requests, lumi_client, json_data_experiments
):
    mock_requests_response.status_code = 200
    data = load_json(json_data_experiments)
    mock_requests_response.json = lambda: data

    experiments_ret = lumi_client.experiments.get_experiments()
    assert experiments_ret is not None


def test_get_experiment_ok(
    mock_requests_response, mock_requests, lumi_client, json_data_experiment
):
    mock_requests_response.status_code = 200
    data = load_json(json_data_experiment)
    mock_requests_response.json = lambda: data
    experiment_ret = lumi_client.experiments.get_experiment("daab39ac-be9f-4de9-87c0-c4c94b297a97")
    assert experiment_ret is not None


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
