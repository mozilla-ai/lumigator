import json
import unittest.mock as mock
from pathlib import Path

LUMI_HOST = "localhost"


def load_json(path: Path) -> str:
    with Path.open(path) as file:
        return json.load(file)


def check_url(is_url, **kwargs):
    assert is_url == kwargs["url"]
    return mock.DEFAULT


def check_method(is_method, **kwargs):
    assert is_method == kwargs["method"]
    return mock.DEFAULT
