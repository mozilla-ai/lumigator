import csv
import io
import os
import uuid
from pathlib import Path
from unittest.mock import Mock, patch

import boto3
import fsspec
import pytest
import requests_mock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fsspec.implementations.memory import MemoryFileSystem
from loguru import logger
from lumigator_schemas.jobs import JobConfig, JobType
from mypy_boto3_s3 import S3Client
from s3fs import S3FileSystem
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from backend.api.deps import get_db_session, get_s3_client, get_s3_filesystem
from backend.api.router import API_V1_PREFIX
from backend.main import create_app
from backend.records.jobs import JobRecord
from backend.repositories.datasets import DatasetRepository
from backend.repositories.jobs import JobRepository, JobResultRepository
from backend.services.datasets import DatasetService
from backend.services.jobs import JobService
from backend.settings import BackendSettings, settings
from backend.tests.fakes.fake_s3 import FakeS3Client

TEST_CAUSAL_MODEL = "hf://hf-internal-testing/tiny-random-LlamaForCausalLM"
TEST_INFER_MODEL = "hf://hf-internal-testing/tiny-random-t5"


def common_resources_dir() -> Path:
    return Path(__file__).parent.parent.parent.parent


def format_dataset(data: list[list[str]]) -> str:
    """Format a list of tabular data as a CSV string."""
    buffer = io.StringIO()
    csv.writer(buffer).writerows(data)
    buffer.seek(0)
    return buffer.read()


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


@pytest.fixture(scope="function")
def dialog_dataset():
    filename = common_resources_dir() / "sample_data" / "dialogsum_exc.csv"
    with Path(filename).open("rb") as f:
        yield f


@pytest.fixture(scope="function")
def dialog_no_gt_dataset():
    filename = common_resources_dir() / "sample_data" / "dialogsum_mini_empty_gt.csv"
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
    fsspec.register_implementation(
        "s3", MemoryFileSystem, clobber=True, errtxt="Failed to register mock S3FS"
    )
    yield MemoryFileSystem()
    logger.info(f"final s3fs contents: {str(MemoryFileSystem.store)}")


@pytest.fixture(scope="function")
def fake_s3_client(fake_s3fs) -> S3Client:
    """Provide a fake S3 client using MemoryFileSystem as underlying storage."""
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    # Please check https://github.com/localstack/localstack/issues/5894
    # for info about the test region used
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"  # pragma: allowlist secret
    os.environ["AWS_ENDPOINT_URL"] = "http://example.com:4566"
    return FakeS3Client(MemoryFileSystem.store)


@pytest.fixture(scope="function")
def boto_s3_client() -> S3Client:
    """Provide a real S3 client."""
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    # Please check https://github.com/localstack/localstack/issues/5894
    # for info about the test region used
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"  # pragma: allowlist secret
    os.environ["AWS_ENDPOINT_URL"] = "http://localhost:4566"
    return boto3.client("s3")


@pytest.fixture(scope="function")
def boto_s3fs() -> S3FileSystem:
    """Provide a real s3fs client."""
    s3fs = S3FileSystem()
    mock_s3fs = Mock(wraps=s3fs)
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
def app_client(app: FastAPI):
    """Create a test client for calling the FastAPI app."""
    base_url = f"http://dev{API_V1_PREFIX}"  # Fake base URL for the app
    with TestClient(app, base_url=base_url) as c:
        yield c


@pytest.fixture(scope="function")
def local_client(app: FastAPI):
    """Create a test client for calling the real backend."""
    base_url = "http://localhost/api/v1/"  # Fake base URL for the app
    with TestClient(app, base_url=base_url) as c:
        yield c


@pytest.fixture(scope="function")
def dependency_overrides_fakes(
    app: FastAPI, db_session: Session, fake_s3_client: S3Client, fake_s3fs: S3FileSystem
) -> None:
    """Override the FastAPI dependency injection for test DB sessions. Uses mocks/fakes for unit tests.

    Reference: https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#override-a-dependency
    """

    def get_db_session_override():
        yield db_session

    def get_s3_client_override():
        yield fake_s3_client

    def get_s3_filesystem_override():
        yield fake_s3fs

    app.dependency_overrides[get_db_session] = get_db_session_override
    app.dependency_overrides[get_s3_client] = get_s3_client_override
    app.dependency_overrides[get_s3_filesystem] = get_s3_filesystem_override


@pytest.fixture(scope="function")
def dependency_overrides_services(
    app: FastAPI, db_session: Session, boto_s3_client: S3Client, boto_s3fs: S3FileSystem
) -> None:
    """Override the FastAPI dependency injection for test DB sessions. Uses real clients for integration tests.

    Reference: https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#override-a-dependency
    """

    def get_db_session_override():
        yield db_session

    def get_s3_client_override():
        yield boto_s3_client

    def get_s3_filesystem_override():
        yield boto_s3fs

    app.dependency_overrides[get_db_session] = get_db_session_override
    app.dependency_overrides[get_s3_client] = get_s3_client_override
    app.dependency_overrides[get_s3_filesystem] = get_s3_filesystem_override


@pytest.fixture(scope="session")
def resources_dir() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def json_data_models(resources_dir) -> Path:
    return resources_dir / "models.json"


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
def dataset_service(db_session, fake_s3_client, fake_s3fs):
    dataset_repo = DatasetRepository(db_session)
    return DatasetService(
        dataset_repo=dataset_repo, s3_client=fake_s3_client, s3_filesystem=fake_s3fs
    )


@pytest.fixture(scope="function")
def job_record(db_session):
    return JobRecord


@pytest.fixture(scope="function")
def job_service(db_session, job_repository, result_repository, dataset_service):
    return JobService(job_repository, result_repository, None, dataset_service)


@pytest.fixture(scope="function")
def backend_settings():
    return BackendSettings()


@pytest.fixture(scope="function")
def create_job_config() -> JobConfig:
    conf_args = {
        "name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
        "model": "hf://facebook/bart-large-cnn",
        "dataset": "016c1f72-4604-48a1-b1b1-394239297e29",
        "max_samples": 10,
        "model_url": "hf://facebook/bart-large-cnn",
        "system_prompt": "Hello Lumigator",
        "config_template": str,
    }

    conf = JobConfig(
        job_id=uuid.uuid4(),
        job_type=JobType.EVALUATION,
        command=settings.EVALUATOR_COMMAND,
        args=conf_args,
    )

    return conf


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


@pytest.fixture(scope="session")
def simple_infer_template():
    return """{{
        "name": "{job_name}/{job_id}",
        "dataset": {{ "path": "{dataset_path}" }},
        "hf_pipeline": {{
            "model_uri": "{model_uri}",
            "task": "{task}",
            "accelerator": "{accelerator}",
            "revision": "{revision}",
            "use_fast": "{use_fast}",
            "trust_remote_code": "{trust_remote_code}",
            "torch_dtype": "{torch_dtype}",
            "max_length": 200
        }},
        "job": {{
            "max_samples": {max_samples},
            "storage_path": "{storage_path}"
        }}
    }}"""
