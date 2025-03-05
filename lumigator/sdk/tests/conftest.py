import json
import sys
import unittest.mock as mock
from http import HTTPStatus
from pathlib import Path
from typing import BinaryIO

import pytest
import requests_mock
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.models import ModelsResponse
from lumigator_sdk.health import Health
from lumigator_sdk.lumigator import LumigatorClient
from urllib3 import Retry

LUMI_HOST = "localhost:8000"

TEST_RETRY = Retry(
    connect=10,
    backoff_factor=1,
    backoff_max=60,
)


@pytest.fixture(scope="function")
def request_mock() -> requests_mock.Mocker:
    with requests_mock.Mocker() as cm:
        yield cm


@pytest.fixture(scope="function")
def lumi_client(request_mock) -> LumigatorClient:
    request_mock.get(
        url=f"http://{LUMI_HOST}/api/v1/{Health.HEALTH_ROUTE}",
        status_code=HTTPStatus.OK,
        json={"status": "OK", "deploymentType": "local"},
    )
    return LumigatorClient(LUMI_HOST)


@pytest.fixture(scope="function")
def lumi_client_int() -> LumigatorClient:
    return LumigatorClient(LUMI_HOST, retry_conf=TEST_RETRY)


@pytest.fixture(scope="session")
def resources_dir() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def common_resources_dir() -> Path:
    return Path(__file__).parent.parent.parent / "sample_data"


@pytest.fixture(scope="session")
def common_resources_sample_data_dir_summarization(common_resources_dir) -> Path:
    return common_resources_dir / "summarization"


@pytest.fixture(scope="session")
def common_resources_sample_data_dir_translation(common_resources_dir) -> Path:
    return common_resources_dir / "translation"


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


@pytest.fixture(
    scope="session",
    params=["experiment-post-all.json", "experiment-post-all-translation.json"],
)
def json_data_experiment_post_all(resources_dir, request) -> Path:
    return resources_dir / request.param


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


@pytest.fixture(
    scope="session",
    params=[
        "job-all-annotation.json",
        "job-all-eval.json",
        "job-all-inference.json",
        "job-all-inference-translation.json",
    ],
)
def json_data_job_all(resources_dir, request) -> Path:
    return resources_dir / request.param


@pytest.fixture(
    scope="session",
    params=[
        "job-minimal-annotation.json",
        "job-minimal-eval.json",
        "job-minimal-inference.json",
    ],
)
def json_data_job_minimal(resources_dir, request) -> Path:
    return resources_dir / request.param


@pytest.fixture(
    scope="session",
    params=["job-extra-annotation.json", "job-extra-eval.json", "job-extra-inference.json"],
)
def json_data_job_extra(resources_dir, request) -> Path:
    return resources_dir / request.param


@pytest.fixture(scope="session")
def json_data_job_submit_response(resources_dir) -> Path:
    return resources_dir / "job-submit-resp.json"


@pytest.fixture(scope="session")
def json_data_job_response(resources_dir) -> Path:
    return resources_dir / "job-resp.json"


@pytest.fixture(scope="session")
def json_data_models() -> ListingResponse[ModelsResponse]:
    """Returns a fake response for the models endpoint,
    to allow for SDK testing of the models endpoint.
    """
    model = {
        "display_name": "facebook/bart-large-cnn",
        "model": "facebook/bart-large-cnn",
        "provider": "hf",
        "description": "BART is a large-sized model fine-tuned on the CNN Daily Mail dataset.",
        "tasks": [
            {
                "summarization": {
                    "max_length": 142,
                    "min_length": 56,
                    "length_penalty": 2.0,
                    "early_stopping": True,
                    "no_repeat_ngram_size": 3,
                    "num_beams": 4,
                }
            }
        ],
        "website_url": "https://huggingface.co/facebook/bart-large-cnn",
    }
    return ListingResponse[ModelsResponse].model_validate({"total": 1, "items": [model]}).model_dump()


@pytest.fixture(scope="function")
def dialog_data(common_resources_sample_data_dir_summarization):
    with Path.open(common_resources_sample_data_dir_summarization / "dialogsum_exc.csv") as file:
        yield file


@pytest.fixture(scope="function")
def dialog_data_unannotated(common_resources_sample_data_dir_summarization):
    with Path.open(common_resources_sample_data_dir_summarization / "dialogsum_mini_no_gt.csv") as file:
        yield file


@pytest.fixture(scope="function")
def long_sequences_data_unannotated(common_resources_sample_data_dir_summarization):
    # Dataset with long sequences
    with Path.open(common_resources_sample_data_dir_summarization / "mock_long_sequences_no_gt.csv") as file:
        yield file


@pytest.fixture(scope="function")
def mock_translation_data(common_resources_sample_data_dir_translation):
    with Path.open(common_resources_sample_data_dir_translation / "sample_translation_en_de.csv") as file:
        yield file


@pytest.fixture(scope="session")
def simple_eval_template():
    return """{{
        "name": "{job_name}/{job_id}",
        "model": {{ "path": "{model_name_or_path}" }},
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
