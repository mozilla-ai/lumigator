import importlib.resources
import json
from pathlib import Path


def test_get_datasets_ok(mock_requests_response, mock_requests, lumi_client):
    mock_requests_response.status_code = 200

    ref = importlib.resources.files("mzai.sdk.tests") / "data/datasets.json"
    with importlib.resources.as_file(ref) as path:
        with Path.open(path) as file:
            data = json.load(file)
            mock_requests_response.json = lambda: data

    datasets_ret = lumi_client.datasets.get_datasets()
    assert datasets_ret is not None
