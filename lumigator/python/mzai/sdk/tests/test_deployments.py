import json
import importlib.resources
import unittest.mock as mock
from http import HTTPStatus
from pathlib import Path

from pytest import raises
from requests.exceptions import HTTPError

from conftest import load_request

def test_get_deployments_ok(mock_requests_response, mock_requests, api_client):
    mock_requests_response.status_code = 200
    data = load_request("data/deployments.json")
    mock_requests_response.json = lambda: data

    deployments_ret = api_client.health.get_deployments()
    assert deployments_ret is not None


