import unittest.mock as mock
import importlib.resources
import json
from pathlib import Path

LUMI_HOST="localhost"

def load_response(mock_requests_response: mock.Mock, path: str):
    ref = importlib.resources.files("sdk.tests") / path
    with importlib.resources.as_file(ref) as path:
        with Path.open(path) as file:
            data = json.load(file)
            mock_requests_response.json = lambda: data

def load_request(path: str) -> str:
    ref = importlib.resources.files("sdk.tests") / path
    with importlib.resources.as_file(ref) as path:
        with Path.open(path) as file:
            return(json.load(file))

def check_url(check_url, **kwargs):
    print(f'the url used is {check_url} vs {kwargs["url"]}')
    assert check_url == kwargs["url"]
    return mock.DEFAULT

