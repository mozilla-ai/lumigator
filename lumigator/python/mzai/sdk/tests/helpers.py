import unittest.mock as mock
import importlib.resources
import json
from importlib.resources.abc import Traversable
from pathlib import Path

LUMI_HOST = "localhost"


def load_response(mock_requests_response: mock.Mock, data_path: Traversable):
    with importlib.resources.as_file(data_path) as path:
        with Path.open(path) as file:
            data = json.load(file)
            mock_requests_response.json = lambda: data


def load_request(data_path: Traversable) -> str:
    with importlib.resources.as_file(data_path) as path:
        with Path.open(path) as file:
            return json.load(file)


def check_url(check_url, **kwargs):
    print(f'the url used is {check_url} vs {kwargs["url"]}')
    assert check_url == kwargs["url"]
    return mock.DEFAULT
