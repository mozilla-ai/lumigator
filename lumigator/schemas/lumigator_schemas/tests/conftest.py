import json
from pathlib import Path

import pytest


def load_json_from_file(file_path: Path) -> dict:
    """Load JSON data from a file path and return it as a dictionary."""
    with Path.open(file_path) as file:
        return json.load(file)


@pytest.fixture(scope="session")
def resources_dir() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def json_workflow_results(resources_dir) -> dict:
    path = resources_dir / "workflow_results.json"
    return load_json_from_file(path)


@pytest.fixture(scope="session")
def json_workflow_results_overlay_all(resources_dir) -> dict:
    path = resources_dir / "workflow_results_overlay_all.json"
    return load_json_from_file(path)


@pytest.fixture(scope="session")
def json_workflow_results_overlay_artifacts_same(resources_dir) -> dict:
    path = resources_dir / "workflow_results_overlay_artifacts_same.json"
    return load_json_from_file(path)


@pytest.fixture(scope="session")
def json_workflow_results_overlay_artifacts_missing(resources_dir) -> dict:
    path = resources_dir / "workflow_results_overlay_artifacts_missing.json"
    return load_json_from_file(path)
