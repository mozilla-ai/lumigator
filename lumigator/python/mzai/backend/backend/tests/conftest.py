import csv
import io
import os
from pathlib import Path

import pytest
import requests_mock
from botocore.exceptions import ClientError
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mypy_boto3_s3 import S3Client
from s3fs import S3FileSystem
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from testcontainers.localstack import LocalStackContainer

from backend.api.deps import get_db_session, get_s3_client
from backend.api.router import API_V1_PREFIX
from backend.main import create_app
from backend.records.jobs import JobRecord, JobResultRecord
from backend.repositories.datasets import DatasetRepository
from backend.repositories.jobs import BaseRepository, JobRepository, JobResultRepository
from backend.services.datasets import DatasetService
from backend.services.jobs import JobService
from backend.settings import BackendSettings, settings
from backend.tests.fakes.fake_ray_client import FakeJobSubmissionClient

# TODO: Break tests into "unit" and "integration" folders based on fixture dependencies


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
    data = [
        ["examples", "ground_truth"],
        ["Hello World", "Hello"],
    ]
    return format_dataset(data)


@pytest.fixture(scope="session")
def valid_experiment_dataset_without_gt() -> str:
    data = [
        ["examples"],
        ["Hello World"],
    ]
    return format_dataset(data)


@pytest.fixture(scope="session")
def missing_examples_dataset() -> str:
    data = [
        ["ground_truth"],
        ["Hello"],
    ]
    return format_dataset(data)


@pytest.fixture(scope="session")
def extra_column_dataset() -> str:
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


@pytest.fixture(scope="session")
def localstack_container():
    """Initialize a LocalStack test container."""
    with LocalStackContainer("localstack/localstack:3.4.0") as localstack:
        yield localstack


@pytest.fixture(scope="session", autouse=True)
def setup_aws(localstack_container: LocalStackContainer):
    """Setup env vars/AWS resources for use with the LocalStack container."""
    # Initialize S3
    s3 = localstack_container.get_client("s3")
    try:
        s3.create_bucket(
            Bucket=settings.S3_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": localstack_container.region_name},
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
            print("Bucket already created, continue")
        else:
            raise e
    # add ENV vars for FSSPEC access to S3 (s3fs + HuggingFace datasets)
    os.environ["FSSPEC_S3_KEY"] = "testcontainers-localstack"
    os.environ["FSSPEC_S3_SECRET"] = "testcontainers-localstack"  # pragma: allowlist secret
    os.environ["FSSPEC_S3_ENDPOINT_URL"] = localstack_container.get_url()
    os.environ["AWS_ACCESS_KEY_ID"] = "testcontainers-localstack"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testcontainers-localstack"  # pragma: allowlist secret
    os.environ["AWS_ENDPOINT_URL"] = localstack_container.get_url()


@pytest.fixture(scope="function")
def s3_client(localstack_container: LocalStackContainer) -> S3Client:
    return localstack_container.get_client("s3")


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


@pytest.fixture(scope="function", autouse=True)
def dependency_overrides(app: FastAPI, db_session: Session, s3_client: S3Client) -> None:
    """Override the FastAPI dependency injection for test DB sessions.

    Reference: https://fastapi.tiangolo.com/he/advanced/testing-database/
    """

    def get_db_session_override():
        yield db_session

    def get_s3_client_override():
        yield s3_client

    app.dependency_overrides[get_db_session] = get_db_session_override
    app.dependency_overrides[get_s3_client] = get_s3_client_override


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
def fake_ray_client():
    return FakeJobSubmissionClient()


@pytest.fixture(scope="function")
def dataset_service(db_session):
    dataset_repo = DatasetRepository(db_session)
    return DatasetService(
        dataset_repo=dataset_repo, s3_client=s3_client, s3_filesystem=S3FileSystem()
    )


@pytest.fixture(scope="function")
def job_record(db_session):
    return JobRecord


@pytest.fixture(scope="function")
def job_service(db_session, job_repository, result_repository, fake_ray_client, dataset_service):
    return JobService(job_repository, result_repository, fake_ray_client, dataset_service)


@pytest.fixture(scope="function")
def backend_settings():
    return BackendSettings()
