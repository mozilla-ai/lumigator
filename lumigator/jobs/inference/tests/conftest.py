import json
import logging
import sys
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


@pytest.fixture(scope="function")
def configure_loguru(caplog):
    """Configures Loguru logging but only for tests that explicitly request it."""

    class PropagateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    # Remove existing handlers but store the config
    existing_handlers = logger._core.handlers.copy()
    logger.remove()
    logger.add(PropagateHandler(), format="{message}")

    yield

    # Restore handlers
    logger.remove()
    for _ in existing_handlers:
        logger.add(sys.stderr, format="{time} {level} {message}")


@pytest.fixture(scope="function")
def caplog_with_loguru(caplog, configure_loguru):
    """Wraps caplog to auto-configure Loguru safely."""
    yield caplog


@pytest.fixture(scope="function")
def api_key() -> str:
    return "12345"
