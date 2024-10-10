import json
import importlib.resources
import unittest.mock as mock
from http import HTTPStatus
from pathlib import Path

from pytest import raises
from requests.exceptions import HTTPError

from tests.helpers import load_json


def test_get_deployments_ok(
    mock_requests_response, mock_requests, lumi_client, json_data_deployments
):
    mock_requests_response.status_code = 200
    data = load_json(json_data_deployments)
    mock_requests_response.json = lambda: data

    deployments_ret = lumi_client.health.get_deployments()
    assert deployments_ret is not None
