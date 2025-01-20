import json
import sys
import unittest.mock as mock
from http import HTTPStatus
from pathlib import Path
from typing import BinaryIO

import pytest
import requests_mock
from lumigator_sdk.completions import Completions
from lumigator_sdk.health import Health
from lumigator_sdk.lumigator import LumigatorClient

LUMI_HOST = "localhost:8000"


@pytest.fixture(scope="function")
def request_mock() -> requests_mock.Mocker:
    with requests_mock.Mocker() as cm:
        yield cm


@pytest.fixture(scope="session")
def mock_vendor_data() -> str:
    return '["openai", "mistral"]'


@pytest.fixture(scope="function")
def lumi_client(request_mock, mock_vendor_data) -> LumigatorClient:
    request_mock.get(
        url=f"http://{LUMI_HOST}/api/v1/{Completions.COMPLETIONS_ROUTE}",
        status_code=HTTPStatus.OK,
        json=json.loads(mock_vendor_data),
    )
    request_mock.get(
        url=f"http://{LUMI_HOST}/api/v1/{Health.HEALTH_ROUTE}",
        status_code=HTTPStatus.OK,
        json={"status": "OK", "deploymentType": "local"},
    )
    return LumigatorClient(LUMI_HOST)


@pytest.fixture(scope="function")
def lumi_client_int() -> LumigatorClient:
    return LumigatorClient(LUMI_HOST)


@pytest.fixture(scope="session")
def resources_dir() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def common_resources_dir() -> Path:
    return Path(__file__).parent.parent.parent / "sample_data"


@pytest.fixture(scope="session")
def json_data_jobs(resources_dir) -> Path:
    return resources_dir / "jobs.json"


@pytest.fixture(scope="session")
def json_data_jobs_submit(resources_dir) -> Path:
    return resources_dir / "jobs-submit.json"


@pytest.fixture(scope="session")
def json_data_job(resources_dir) -> Path:
    return resources_dir / "job.json"


@pytest.fixture(scope="session")
def json_data_job_extra(resources_dir) -> Path:
    return resources_dir / "job-extra.json"


@pytest.fixture(scope="session")
def json_data_experiments(resources_dir) -> Path:
    return resources_dir / "experiments.json"


@pytest.fixture(scope="session")
def json_data_experiment(resources_dir) -> Path:
    return resources_dir / "experiment.json"


@pytest.fixture(scope="session")
def json_data_experiment_missing(resources_dir) -> Path:
    return resources_dir / "experiment-missing.json"


@pytest.fixture(scope="session")
def json_data_experiment_post_response(resources_dir) -> Path:
    return resources_dir / "experiment-post-response.json"


@pytest.fixture(scope="session")
def json_data_experiment_post_simple(resources_dir) -> Path:
    return resources_dir / "experiment-post-simple.json"


@pytest.fixture(scope="session")
def json_data_experiment_post_all(resources_dir) -> Path:
    return resources_dir / "experiment-post-all.json"


@pytest.fixture(scope="session")
def json_data_experiment_result(resources_dir) -> Path:
    return resources_dir / "experiment-result.json"


@pytest.fixture(scope="session")
def json_data_experiment_result_missing(resources_dir) -> Path:
    return resources_dir / "experiment-result-no-experiment.json"


@pytest.fixture(scope="session")
def json_data_experiment_result_download(resources_dir) -> Path:
    return resources_dir / "experiment-download.json"


@pytest.fixture(scope="session")
def json_data_experiment_result_download_missing(resources_dir) -> Path:
    return resources_dir / "experiment-download-no-experiment.json"


@pytest.fixture(scope="session")
def json_data_datasets(resources_dir) -> Path:
    return resources_dir / "datasets.json"


@pytest.fixture(scope="session")
def json_data_dataset(resources_dir) -> Path:
    return resources_dir / "dataset.json"


@pytest.fixture(scope="session")
def json_data_job_all(resources_dir) -> Path:
    return resources_dir / "job-all.json"


@pytest.fixture(scope="session")
def json_data_job_minimal(resources_dir) -> Path:
    return resources_dir / "job-minimal.json"


@pytest.fixture(scope="session")
def json_data_job_submit_response(resources_dir) -> Path:
    return resources_dir / "job-submit-resp.json"


@pytest.fixture(scope="session")
def json_data_job_response(resources_dir) -> Path:
    return resources_dir / "job-resp.json"


@pytest.fixture(scope="session")
def json_data_models(resources_dir) -> Path:
    return resources_dir / "models.json"


@pytest.fixture(scope="function")
def dialog_data(common_resources_dir):
    with Path.open(common_resources_dir / "dialogsum_exc.csv") as file:
        yield file


@pytest.fixture(scope="session")
def simple_eval_template():
    return """{{
        "name": "{job_name}/{job_id}",
        "model": {{ "path": "{model_uri}" }},
        "dataset": {{ "path": "{dataset_path}" }},
        "evaluation": {{
            "metrics": ["meteor", "rouge"],
            "use_pipeline": false,
            "max_samples": {max_samples},
            "return_input_data": true,
            "return_predictions": true,
            "storage_path": "{storage_path}"
        }}
    }}"""
