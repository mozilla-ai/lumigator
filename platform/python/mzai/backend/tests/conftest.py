import os
from unittest import mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from testcontainers.localstack import LocalStackContainer
from testcontainers.postgres import PostgresContainer

from mzai.backend.api.deps import get_db_session
from mzai.backend.api.router import API_V1_PREFIX
from mzai.backend.main import create_app
from mzai.backend.records.base import BaseRecord

# TODO: Break tests into "unit" and "integration" folders based on fixture dependencies


@pytest.fixture(scope="session")
def localstack():
    """Initialize a LocalStack test container."""
    with LocalStackContainer("localstack/localstack:3.4.0", region_name="us-east-2") as localstack:
        yield localstack


@pytest.fixture(scope="session")
def postgres():
    """Initialize a Postgres test container."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session", autouse=True)
def setup_aws(localstack: LocalStackContainer):
    """Setup env vars/AWS resources for use with the LocalStack container."""
    # Initialize S3
    bucket_name = "test-bucket"
    s3 = localstack.get_client("s3")
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": localstack.region_name},
    )
    # Patch env vars for BackendSettings
    localstack_env_vars = {
        "S3_BUCKET": bucket_name,
        "S3_PORT": str(localstack.edge_port),
        "AWS_HOST": localstack.get_container_host_ip(),
        "AWS_DEFAULT_REGION": localstack.region_name,
    }
    with mock.patch.dict(os.environ, localstack_env_vars):
        yield


@pytest.fixture(scope="session")
def db_engine(postgres: PostgresContainer):
    """Initialize a DB engine bound to the Postres container, and create tables."""
    engine = create_engine(postgres.get_connection_url(), echo=True)

    # TODO: Run migrations here once switched over to Alembic.
    BaseRecord.metadata.create_all(engine)

    # Patch env vars for BackendSettings
    # In theory it shouldnt matter because tests run off the test DB engine, but just in case
    postgres_env_vars = {
        "POSTGRES_PORT": str(postgres.port),
        "POSTGRES_USER": postgres.username,
        "POSTGRES_PASSWORD": postgres.password,
        "POSTGRES_DB": postgres.dbname,
    }
    with mock.patch.dict(os.environ, postgres_env_vars):
        yield engine


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
def app(db_engine: Engine):
    """Create the FastAPI app bound to the test DB engine."""
    app = create_app(db_engine)
    return app


@pytest.fixture(scope="function")
def app_client(app: FastAPI):
    """Create a test client for calling the FastAPI app."""
    base_url = f"http://mzai.dev{API_V1_PREFIX}"  # Fake base URL for the app
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
