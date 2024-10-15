from .helpers import load_json


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


def test_get_experiment_missing(
    mock_requests_response, mock_requests, lumi_client, json_data_experiment_missing
):
    mock_requests_response.status_code = 404
    data = load_json(json_data_experiment_missing)
    mock_requests_response.json = lambda: data
    experiment_ret = lumi_client.experiments.get_experiment("daab39ac-be9f-4de9-87c0-c4c94b297a97")
    assert experiment_ret is None


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


def test_get_experiment_result_ok(
    mock_requests_response, mock_requests, lumi_client, json_data_experiment_result
):
    mock_requests_response.status_code = 200
    data = load_json(json_data_experiment_result)
    mock_requests_response.json = lambda: data

    experiment_id = "1e23ed9f-b193-444e-8427-e2119a08b0d8"
    response = lumi_client.experiments.get_experiment_result(experiment_id)
    assert response is not None
    assert str(response.experiment_id) == experiment_id
    assert str(response.id) == "e3be6e4b-dd1e-43b7-a97b-0d47dcc49a4f"


def test_get_experiment_result_no_experiment(
    mock_requests_response, mock_requests, lumi_client, json_data_experiment_result_missing
):
    mock_requests_response.status_code = 404
    data = load_json(json_data_experiment_result_missing)
    mock_requests_response.json = lambda: data

    # TODO: The return from the API at the time of creating the test is
    # incorrect and contains malformed error details.
    # Once the API bug is corrected the associated data for this test should
    # be updated.
    # See: data/experiment-download-no-experiment.json
    experiment_id = "1e23ed9f-b193-444e-8427-e2119a08b0d8"
    response = lumi_client.experiments.get_experiment_result(experiment_id)
    assert response is None


def test_get_experiment_result_download_ok(
    mock_requests_response, mock_requests, lumi_client, json_data_experiment_result_download
):
    mock_requests_response.status_code = 200
    data = load_json(json_data_experiment_result_download)
    mock_requests_response.json = lambda: data

    experiment_id = "1e23ed9f-b193-444e-8427-e2119a08b0d8"
    response = lumi_client.experiments.get_experiment_result_download(experiment_id)
    assert response is not None

    assert str(response.download_url) == "http://mozilla.ai/results/some-result.csv?X-Key=ABCDEF"
    assert str(response.id) == experiment_id


def test_get_experiment_result_download_no_experiment(
    mock_requests_response, mock_requests, lumi_client, json_data_experiment_result_download_missing
):
    mock_requests_response.status_code = 404
    data = load_json(json_data_experiment_result_download_missing)
    mock_requests_response.json = lambda: data

    experiment_id = "1e23ed9f-b193-444e-8427-e2119a08b0d8"
    response = lumi_client.experiments.get_experiment_result_download(experiment_id)
    assert response is None
