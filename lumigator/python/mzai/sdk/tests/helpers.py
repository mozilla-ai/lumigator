import unittest.mock as mock
import importlib.resources
import json
from pathlib import Path
from importlib.resources.abc import Traversable


LUMI_HOST = "localhost"


def load_json(datafile: Traversable) -> str:
    with importlib.resources.as_file(datafile) as path:
        with Path.open(path) as file:
            return json.load(file)


def check_url(is_url, **kwargs):
    assert is_url == kwargs["url"]
    return mock.DEFAULT


def check_method(is_method, **kwargs):
    assert is_method == kwargs["method"]
    return mock.DEFAULT
