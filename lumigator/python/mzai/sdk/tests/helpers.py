import unittest.mock as mock
import importlib.resources
import json
from pathlib import Path

LUMI_HOST = "localhost"


def load_response(mock_requests_response: mock.Mock, datafile: str):
    with importlib.resources.as_file(datafile) as path:
        with Path.open(path) as file:
            data = json.load(file)
            mock_requests_response.json = lambda: data


def load_request(datafile: str) -> str:
    with importlib.resources.as_file(datafile) as path:
        with Path.open(path) as file:
            return json.load(file)


def check_url(check_url, **kwargs):
    assert check_url == kwargs["url"]
    return mock.DEFAULT
