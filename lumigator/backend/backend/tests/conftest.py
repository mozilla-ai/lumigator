import csv
import io
import json
import logging
import os
import sys
import time
import uuid
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID

import evaluator
import fastapi
import fsspec
import pytest
import requests_mock
import yaml
from fastapi import FastAPI, UploadFile
from fastapi.testclient import TestClient
from fsspec.implementations.memory import MemoryFileSystem
from inference.definition import JobDefinitionInference
from loguru import logger
from lumigator_schemas.experiments import GetExperimentResponse
from lumigator_schemas.jobs import (
    JobConfig,
    JobResponse,
    JobStatus,
    JobType,
)
from lumigator_schemas.models import ModelsResponse
from mlflow.entities import Metric, Param, Run, RunData, RunInfo, RunTag
from pydantic import PositiveInt
from s3fs import S3FileSystem
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from backend.api.deps import get_db_session, get_job_service, get_s3_filesystem
from backend.api.router import API_V1_PREFIX
from backend.main import create_app
from backend.records.jobs import JobRecord
from backend.repositories.datasets import DatasetRepository
from backend.repositories.jobs import JobRepository, JobResultRepository
from backend.repositories.secrets import SecretRepository
from backend.services.datasets import DatasetService
from backend.services.jobs import JobService
from backend.services.secrets import SecretService
from backend.services.workflows import WorkflowService
from backend.settings import BackendSettings, settings
from backend.tests.fakes.fake_s3 import FakeS3Client
from backend.tracking.mlflow import MLflowTrackingClient

TEST_SEQ2SEQ_MODEL = "hf-internal-testing/tiny-random-BARTForConditionalGeneration"
TEST_CAUSAL_MODEL = "hf-internal-testing/tiny-random-LlamaForCausalLM"
MODELS_PATH = Path(__file__).resolve().parents[1] / "models.yaml"

# The recommended default value for the maximum amount of polls to carry out
# in order to determine whether a task finished or not.
DEFAULT_MAX_RETRIES = 18

# The recommended default value for the interval between polls/retries in seconds.
DEFAULT_RETRY_INTERVAL_SECONDS = 10

# Maximum time we should allow test jobs to run
MAX_JOB_TIMEOUT_SECS = 60 * 5


@pytest.fixture(scope="session")
def background_tasks() -> BackgroundTasks:
    return BackgroundTasks()


@pytest.fixture(scope="function")
def disable_background_tasks(monkeypatch):
    """Patches background tasks' ``add_task`` method as a no-op.

    Useful for testing purposes to disable background tasks inside a ``TestClient``.
    Background tasks run asynchronously in normal operation, but when using ``TestClient`` they
    become synchronous, causing tests to wait for them to complete before exiting.
    """

    def noop_add_task(self, func, *args, **kwargs):
        pass

    monkeypatch.setattr(fastapi.BackgroundTasks, "add_task", noop_add_task)


@pytest.fixture(scope="session")
def common_resources_dir() -> Path:
    return Path(__file__).parent.parent.parent.parent


@pytest.fixture(scope="session")
def common_resources_sample_data_dir(common_resources_dir) -> Path:
    return common_resources_dir / "sample_data"


@pytest.fixture(scope="session")
def common_resources_sample_data_dir_summarization(common_resources_sample_data_dir) -> Path:
    return common_resources_sample_data_dir / "summarization"


@pytest.fixture(scope="session")
def common_resources_sample_data_dir_translation(common_resources_sample_data_dir) -> Path:
    return common_resources_sample_data_dir / "translation"


def format_dataset(data: list[list[str]]) -> str:
    """Format a list of tabular data as a CSV string."""
    buffer = io.StringIO()
    csv.writer(buffer).writerows(data)
    buffer.seek(0)
    return buffer.read()


def wait_for_job(
    client: TestClient,
    job_id: UUID,
    max_retries: PositiveInt = DEFAULT_MAX_RETRIES,
    retry_interval: PositiveInt = DEFAULT_RETRY_INTERVAL_SECONDS,
) -> bool:
    """Attempts to wait for the specified job to finish and returns True if it succeeded.

    :param client: The test client to use for making requests.
    :param job_id: The ID of the job to wait for.
    :param max_retries: The maximum number of retries to perform before timing out.
    :param retry_interval: The interval in seconds between retries.
    :return: True if the job succeeded, False if it failed.
    :raises TimeoutError: If the job does not reach a finished state within the specified max retries.
    """
    for _ in range(max_retries):
        response = client.get(f"/jobs/{job_id}")
        assert response.status_code == 200
        job_status = JobResponse.model_validate(response.json()).status

        if job_status in JobService.TERMINAL_STATUS:
            return job_status == JobStatus.SUCCEEDED.value
        time.sleep(retry_interval)

    raise TimeoutError("Job poll timed out")


def wait_for_experiment(
    client: TestClient,
    experiment_id: UUID,
    max_retries: PositiveInt = DEFAULT_MAX_RETRIES,
    retry_interval: PositiveInt = DEFAULT_RETRY_INTERVAL_SECONDS,
) -> bool:
    """Attempts to wait for the specified experiment to finish and returns True if it succeeded.

    :param client: The test client to use for making requests.
    :param experiment_id: The ID of the experiment to wait for.
    :param max_retries: The maximum number of retries to perform before timing out.
    :param retry_interval: The interval in seconds between retries.
    :return: True if the experiment succeeded, False if it failed.
    :raises TimeoutError: If the experiment does not reach a finished state within the specified max retries.
    """
    for _ in range(max_retries):
        response = client.get(f"/experiments/{experiment_id}")
        assert response.status_code == 200
        experiment_status = GetExperimentResponse.model_validate(response.json()).status

        if experiment_status in JobService.TERMINAL_STATUS:
            return experiment_status == JobStatus.SUCCEEDED.value
        time.sleep(retry_interval)

    raise TimeoutError("Experiment poll timed out")


@pytest.fixture
def valid_experiment_dataset() -> str:
    """Minimal valid dataset with groundtruth."""
    data = [
        ["examples", "ground_truth"],
        ["Hello World", "Hello"],
    ]
    return format_dataset(data)


@pytest.fixture(scope="session")
def valid_experiment_dataset_without_gt() -> str:
    """Minimal valid dataset without groundtruth."""
    data = [
        ["examples"],
        ["Hello World"],
    ]
    return format_dataset(data)


@pytest.fixture
def valid_upload_file(valid_experiment_dataset) -> UploadFile:
    """Minimal valid upload file (with ground truth)."""
    fake_filename = "dataset.csv"
    fake_file = io.BytesIO(valid_experiment_dataset.encode("utf-8"))
    fake_upload_file = UploadFile(
        filename=fake_filename,
        file=fake_file,
    )
    return fake_upload_file


@pytest.fixture(scope="session")
def valid_experiment_dataset_with_empty_gt() -> str:
    """Minimal valid dataset without groundtruth."""
    data = [
        ["examples", "ground_truth"],
        ["Hello World"],
    ]
    return format_dataset(data)


@pytest.fixture(scope="session")
def missing_examples_dataset() -> str:
    """Minimal invalid dataset without examples."""
    data = [
        ["ground_truth"],
        ["Hello"],
    ]
    return format_dataset(data)


@pytest.fixture(scope="session")
def extra_column_dataset() -> str:
    """Minimal valid dataset with groundtruth and extra fields."""
    data = [
        ["examples", "ground_truth", "extra"],
        ["Hello World", "Hello", "Nope"],
    ]
    return format_dataset(data)


@pytest.fixture(scope="session")
def dialog_dataset(common_resources_sample_data_dir_summarization):
    filename = common_resources_sample_data_dir_summarization / "dialogsum_exc.csv"
    with Path(filename).open("rb") as f:
        yield f


@pytest.fixture(scope="function")
def dialog_empty_gt_dataset(common_resources_sample_data_dir_summarization):
    filename = common_resources_sample_data_dir_summarization / "dialogsum_mini_empty_gt.csv"
    with Path(filename).open("rb") as f:
        yield f


@pytest.fixture(scope="function")
def dialog_no_gt_dataset(common_resources_sample_data_dir_summarization):
    filename = common_resources_sample_data_dir_summarization / "dialogsum_mini_no_gt.csv"
    with Path(filename).open("rb") as f:
        yield f


@pytest.fixture(scope="session")
def mock_translation_dataset(common_resources_sample_data_dir_translation):
    filename = common_resources_sample_data_dir_translation / "sample_translation_en_de.csv"
    with Path(filename).open("rb") as f:
        yield f


@pytest.fixture(scope="session", autouse=True)
def db_engine():
    """Initialize a DB engine and create tables."""
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, echo=True)
    return engine


@pytest.fixture(scope="function")
def db_session(db_engine: Engine):
    """Fixture to provide a clean DB session per test function.

    This method yields a session and rolls it back after test completion
    so tests do not actually alter the DB state (which is initialized once per test suite).

    Reference: https://dev.to/jbrocher/fastapi-testing-a-database-5ao5
    """
    with db_engine.begin() as connection:
        try:
            session = Session(bind=connection)
            yield session
        finally:
            session.rollback()


@pytest.fixture(scope="function")
def fake_s3fs() -> S3FileSystem:
    """Replace the filesystem registry for S3 with a MemoryFileSystem implementation."""
    fsspec.register_implementation("s3", MemoryFileSystem, clobber=True, errtxt="Failed to register mock S3FS")
    mfs = MemoryFileSystem()
    mfs_mock = MagicMock(wraps=mfs)
    mfs_mock.s3 = FakeS3Client(MemoryFileSystem.store)
    # Mock the find method to match the path (minus the S3:// prefix)
    # and be a bit less strict about just seeing the prefix in the path in general.
    mfs_mock.find = lambda path, prefix: [
        k for k in MemoryFileSystem.store.keys() if k.removeprefix("s3://").startswith(path) and k.find(prefix) != -1
    ]

    yield mfs_mock
    logger.info(f"final s3fs contents: {str(MemoryFileSystem.store)}")


@pytest.fixture(scope="function")
def boto_s3fs() -> Generator[S3FileSystem, None, None]:
    """Provide a real s3fs client wrapped with a mock to intercept calls."""
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID", "lumigator")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "lumigator")
    aws_endpoint_url = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:9000")
    aws_default_region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")

    # Mock the S3 'storage_options' property to match the real client.
    s3fs = S3FileSystem(
        key=aws_access_key_id,
        secret=aws_secret_access_key,
        endpoint_url=aws_endpoint_url,
        client_kwargs={"region_name": aws_default_region},
    )

    mock_s3fs = MagicMock(
        wraps=s3fs,
        storage_options={
            "client_kwargs": {"region_name": aws_default_region},
            "key": aws_access_key_id,
            "secret": aws_secret_access_key,
            "endpoint_url": aws_endpoint_url,
        },
    )

    yield mock_s3fs
    logger.info(f"intercepted s3fs calls: {str(mock_s3fs.mock_calls)}")


@pytest.fixture(scope="session")
def app():
    """Create the FastAPI app bound to DB managed via Alembic.

    Expects an environment variable of 'SQLALCHEMY_DATABASE_URL' to be configured.
    Ideally this should be an absolute path:

    e.g. sqlite:////Users/{me}/tmp/local_test.db

    If the environment variable is not specified, then a 'local.db' will be created in the
    folder where the tests are executed.
    """
    app = create_app()
    return app


@pytest.fixture(scope="function")
def test_client(app: FastAPI) -> Generator[TestClient, Any, None]:
    """Create a test client for calling the FastAPI app directly."""
    base_url = "http://localhost/api/v1/"  # Fake base URL for the app, mainly for display purposes.
    with TestClient(app, base_url=base_url) as c:
        yield c


@pytest.fixture(scope="function")
def test_client_without_background_tasks(app: FastAPI, disable_background_tasks) -> Generator[TestClient, Any, None]:
    """Create a test client that directly calls FastAPI, with background tasks 'disabled'.

    Any underlying call in the application's code to `add_task` will return immediately (no-op).
    This is useful for testing when you don't need background tasks to complete, and you want to avoid waiting for them.
    """
    base_url = "http://localhost/api/v1/"  # Fake base URL, mainly for display purposes.
    with TestClient(app, base_url=base_url) as c:
        yield c


@pytest.fixture(scope="function")
def dependency_overrides_fakes(app: FastAPI, db_session: Session, fake_s3fs: S3FileSystem) -> None:
    """Override the FastAPI dependency injection for test DB sessions. Uses mocks/fakes for unit tests.

    Reference: https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#override-a-dependency
    """

    def get_db_session_override():
        yield db_session

    def get_s3_filesystem_override():
        yield fake_s3fs

    app.dependency_overrides[get_db_session] = get_db_session_override
    app.dependency_overrides[get_s3_filesystem] = get_s3_filesystem_override


@pytest.fixture(scope="function")
def dependency_overrides_services(app: FastAPI, db_session: Session, boto_s3fs: S3FileSystem) -> None:
    """Override the FastAPI dependency injection for test DB sessions. Uses real clients for integration tests.

    Reference: https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#override-a-dependency
    """

    def get_db_session_override():
        yield db_session

    def get_s3_filesystem_override():
        yield boto_s3fs

    app.dependency_overrides[get_db_session] = get_db_session_override
    app.dependency_overrides[get_s3_filesystem] = get_s3_filesystem_override


@pytest.fixture(scope="session")
def resources_dir() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def json_ray_version(resources_dir) -> Path:
    return resources_dir / "ray_version.json"


@pytest.fixture(scope="session")
def json_data_health_job_metadata_ok(resources_dir) -> Path:
    return resources_dir / "health_job_metadata.json"


@pytest.fixture(scope="session")
def json_data_health_job_metadata_ray(resources_dir) -> Path:
    return resources_dir / "health_job_metadata_ray.json"


@pytest.fixture(scope="function")
def request_mock() -> requests_mock.Mocker:
    with requests_mock.Mocker() as cm:
        yield cm


@pytest.fixture(scope="function")
def job_repository(db_session):
    return JobRepository(session=db_session)


@pytest.fixture(scope="function")
def result_repository(db_session):
    return JobResultRepository(session=db_session)


@pytest.fixture(scope="function")
def dataset_service(db_session, fake_s3fs):
    dataset_repo = DatasetRepository(db_session)
    return DatasetService(dataset_repo=dataset_repo, s3_filesystem=fake_s3fs)


@pytest.fixture(scope="function")
def secret_repository(db_session):
    return SecretRepository(db_session)


@pytest.fixture(scope="session")
def secret_key() -> str:
    return os.environ.get(
        "LUMIGATOR_SECRET_KEY",
        "7yz2E+qwV3TCg4xHTlvXcYIO3PdifFkd1urv2F/u/5o=",  # pragma: allowlist secret
    )


@pytest.fixture(scope="function")
def secret_service(db_session, secret_repository, secret_key):
    return SecretService(secret_key=secret_key, secret_repo=secret_repository)


@pytest.fixture(scope="function")
def tracking_client():
    return MagicMock()


@pytest.fixture(scope="function")
def workflow_service(job_repository, job_service, dataset_service, background_tasks, secret_service, tracking_client):
    return WorkflowService(
        job_repository, job_service, dataset_service, background_tasks, secret_service, tracking_client
    )


@pytest.fixture(scope="function")
def job_record(db_session):
    return JobRecord


@pytest.fixture(scope="function")
def job_service(db_session, job_repository, result_repository, dataset_service, secret_service, background_tasks):
    return JobService(job_repository, result_repository, None, dataset_service, secret_service, background_tasks)


@pytest.fixture(scope="function")
def job_service_dependency_override(app: FastAPI, job_service) -> None:
    def get_job_service_override():
        yield job_service

    app.dependency_overrides[get_job_service] = get_job_service_override


@pytest.fixture(scope="function")
def backend_settings():
    return BackendSettings()


@pytest.fixture(scope="function")
def create_job_config() -> JobConfig:
    conf_args = {
        "name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
        "model": "hf-internal-testing/tiny-random-BARTForConditionalGeneration",
        "provider": "hf",
        "dataset": "016c1f72-4604-48a1-b1b1-394239297e29",
        "max_samples": 10,
        "base_url": None,
        "system_prompt": "Hello Lumigator",
        "config_template": str,
    }

    conf = JobConfig(
        job_id=uuid.uuid4(),
        job_type=evaluator.definition.EVALUATOR_JOB_DEFINITION.type,
        command=evaluator.definition.EVALUATOR_JOB_DEFINITION.command,
        args=conf_args,
    )

    return conf


@pytest.fixture(scope="session")
def simple_eval_template():
    return """{{
        "name": "{job_name}/{job_id}",
        "model": {{ "path": "{model_name_or_path}" }},
        "dataset": {{ "path": "{dataset_path}" }},
        "evaluation": {{
            "metrics": ["meteor", "rouge"],
            "max_samples": {max_samples},
            "return_input_data": true,
            "return_predictions": true,
            "storage_path": "{storage_path}"
        }}
    }}"""


@pytest.fixture(scope="session")
def simple_infer_template():
    return """{{
        "name": "{job_name}/{job_id}",
        "dataset": {{ "path": "{dataset_path}" }},
        "hf_pipeline": {{
            "model_name_or_path": "{model_name_or_path}",
            "task": "{task}",
            "accelerator": "{accelerator}",
            "revision": "{revision}",
            "use_fast": "{use_fast}",
            "trust_remote_code": "{trust_remote_code}",
            "torch_dtype": "{torch_dtype}"
        }},
        "job": {{
            "max_samples": {max_samples},
            "storage_path": "{storage_path}"
        }}
    }}"""


@pytest.fixture
def job_definition_fixture():
    return JobDefinitionInference(
        command=MagicMock(spec=str),
        pip_reqs=MagicMock(spec=list),
        work_dir=MagicMock(spec=str),
        config_model=MagicMock(spec=dict),
        type=JobType.INFERENCE,
    )


@pytest.fixture(scope="function")
def model_specs_data() -> list[ModelsResponse]:
    """Fixture that loads and returns the YAML data."""
    with Path(MODELS_PATH).open() as file:
        model_specs = yaml.safe_load(file)

    models = [ModelsResponse.model_validate(item) for item in model_specs]

    return models


@pytest.fixture(scope="function")
def fake_mlflow_tracking_client(fake_s3fs):
    """Fixture for MLflowTrackingClient using the real MLflowClient."""
    return MLflowTrackingClient(tracking_uri="http://mlflow.mock", s3_file_system=fake_s3fs)


@pytest.fixture(scope="session")
def json_mlflow_runs_search_single(resources_dir) -> dict:
    path = resources_dir / "mlflow_runs_search_single.json"
    with Path.open(path) as file:
        return json.load(file)


@pytest.fixture
def sample_mlflow_run():
    """Fixture for a sample MlflowRun with mock data."""
    return Run(
        run_info=RunInfo(
            run_uuid="d34dbeef-1000-0000-0000-000000000000",
            experiment_id="exp-1",
            user_id="user",
            status="FINISHED",
            start_time=123456789,
            end_time=None,
            lifecycle_stage="active",
            artifact_uri="",
        ),
        run_data=RunData(
            metrics=[
                Metric(key="accuracy", value=0.75, timestamp=123456789, step=0),
            ],
            params=[
                Param(key="batch_size", value="32"),
            ],
            tags=[
                RunTag(key="description", value="A sample workflow"),
                RunTag(key="mlflow.runName", value="Run2"),
                RunTag(key="model", value="SampleModel"),
                RunTag(key="system_prompt", value="Prompt text"),
                RunTag(key="status", value="COMPLETED"),
            ],
        ),
    )


@pytest.fixture
def fake_mlflow_run_deleted():
    """Fixture for a deleted MLflow run."""
    run_info = RunInfo(
        run_uuid="d34dbeef-1000-0000-0000-000000000000",
        experiment_id="exp-456",
        user_id="user-789",
        status="FAILED",
        start_time=int(datetime(2024, 1, 1).timestamp() * 1000),
        end_time=None,
        lifecycle_stage="deleted",
        artifact_uri="s3://some-bucket",
    )

    run_data = RunData(metrics={}, params={}, tags={})

    return Run(run_info=run_info, run_data=run_data)
