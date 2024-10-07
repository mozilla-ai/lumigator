from pathlib import Path

from tests.helpers import load_request

def test_get_datasets_ok(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200
    data = load_request("data/datasets.json")
    mock_requests_response.json = lambda: data

    datasets_ret = lumi_client.datasets.get_datasets()
    assert datasets_ret is not None
