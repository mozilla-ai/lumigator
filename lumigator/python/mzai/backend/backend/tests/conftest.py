import json
import os
from pathlib import Path

import pytest
import requests_mock
from botocore.exceptions import ClientError
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from testcontainers.localstack import LocalStackContainer

from backend.api.deps import get_db_session
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
def dependency_overrides(app: FastAPI, db_session: Session) -> None:
    """Override the FastAPI dependency injection for test DB sessions.

    Reference: https://fastapi.tiangolo.com/he/advanced/testing-database/
    """

    def get_db_session_override():
        yield db_session

    app.dependency_overrides[get_db_session] = get_db_session_override


@pytest.fixture(scope="session")
def resources_dir() -> Path:
    return Path(__file__).parent / "data"


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
