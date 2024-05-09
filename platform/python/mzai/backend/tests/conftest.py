import os
from unittest import mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session
from testcontainers.localstack import LocalStackContainer
from testcontainers.postgres import PostgresContainer

from mzai.backend.api.deps import get_db_session, get_s3_client
from mzai.backend.api.router import API_V1_PREFIX
from mzai.backend.main import create_app
from mzai.backend.records.base import BaseRecord
from mzai.backend.settings import settings
from mzai.backend.types import S3Client

# TODO: Break tests into "unit" and "integration" folders based on fixture dependencies


@pytest.fixture(scope="session")
def postgres_container():
    """Initialize a Postgres test container."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session", autouse=True)
def db_engine(postgres_container: PostgresContainer):
    """Initialize a DB engine bound to the Postres container, and create tables."""
    engine = create_engine(postgres_container.get_connection_url(), echo=True)

    # TODO: Run migrations here once switched over to Alembic.
    BaseRecord.metadata.create_all(engine)

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
    s3.create_bucket(
        Bucket=settings.S3_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": localstack_container.region_name},
    )


@pytest.fixture(scope="function")
def s3_client(localstack_container: LocalStackContainer) -> S3Client:
    return localstack_container.get_client("s3")


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
