import os
import uuid
from pathlib import Path

import pytest
from botocore.exceptions import ClientError
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mypy_boto3_s3 import S3Client
from schemas.jobs import JobConfig, JobType
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from testcontainers.localstack import LocalStackContainer

from backend.api.deps import get_db_session, get_s3_client
from backend.api.router import API_V1_PREFIX
from backend.main import create_app
from backend.settings import settings

# TODO: Break tests into "unit" and "integration" folders based on fixture dependencies

def common_resources_dir() -> Path:
    return Path(__file__).parent.parent.parent.parent

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
    os.environ["FSSPEC_S3_SECRET"] = "testcontainers-localstack" # pragma: allowlist secret
    os.environ["FSSPEC_S3_ENDPOINT_URL"] = localstack_container.get_url()
    os.environ["AWS_ACCESS_KEY_ID"] = "testcontainers-localstack"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testcontainers-localstack" # pragma: allowlist secret
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

@pytest.fixture(scope="function")
def create_job_config()-> JobConfig:
    conf_args = {
        "name": "test_run_hugging_face",
        "description": "Test run for Huggingface model",
        "model": "hf://facebook/bart-large-cnn",
        "dataset": "016c1f72-4604-48a1-b1b1-394239297e29",
        "max_samples": 10,
        "model_url": "hf://facebook/bart-large-cnn",
        "system_prompt": "Hello Lumigator",
        "config_template": {},
    }

    conf = JobConfig(
        job_id=uuid.uuid4(),
        job_type=JobType.EVALUATION,
        command=settings.EVALUATOR_COMMAND,
        args=conf_args ,
    )


    return conf
