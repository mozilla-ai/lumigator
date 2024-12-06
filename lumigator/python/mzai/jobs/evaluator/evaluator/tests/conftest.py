import json
from pathlib import Path

import pytest


def load_json(path: Path) -> dict:
    with Path.open(path) as file:
        return json.load(file)


def resources_dir() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def json_config_minimal() -> dict:
    return load_json(resources_dir() / "config_minimal.json")


@pytest.fixture(scope="session")
def json_config_full() -> dict:
    return load_json(resources_dir() / "config_full.json")
