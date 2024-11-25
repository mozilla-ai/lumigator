from pytest import raises
from requests.exceptions import HTTPError
from tests.helpers import load_json


def test_sdk_suggested_models_ok(
    mock_requests_response, mock_requests, lumi_client, json_data_models
):
    mock_requests_response.status_code = 200
    data = load_json(json_data_models)
    mock_requests_response.json = lambda: data

    models = lumi_client.models.get_suggested_models("summarization")
    assert models is not None
    assert len(models.items) == models.total


def test_sdk_suggested_models_invalid_task(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 400
    error = HTTPError(response=mock_requests_response)
    mock_requests.side_effect = error

    with raises(HTTPError):
        lumi_client.models.get_suggested_models("invalid_task")
