import json
import logging
from pathlib import Path

import pytest
from loguru import logger
from model_clients.external_api_clients import LiteLLMModelClient


def load_json(path: Path) -> dict:
    with Path.open(path) as file:
        return json.load(file)


def resources_dir() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def json_config_minimal() -> dict:
    return load_json(resources_dir() / "config_minimal.json")


@pytest.fixture(scope="session")
def json_config_full_api() -> dict:
    return load_json(resources_dir() / "config_full_api.json")


@pytest.fixture(scope="session")
def json_config_full_hf() -> dict:
    return load_json(resources_dir() / "config_full_hf.json")


@pytest.fixture(autouse=True)
def configure_loguru(caplog):
    class PropagateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    logger.remove()
    logger.add(PropagateHandler(), format="{message}")
    yield
    logger.remove()


@pytest.fixture(scope="function")
def api_key() -> str:
    return "12345"
