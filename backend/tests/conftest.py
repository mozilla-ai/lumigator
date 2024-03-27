import pytest
import sqlalchemy
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from src.api.deps import get_db_session
from src.db import BaseRecord, DatabaseSessionManager
from src.main import create_app
from src.settings import settings


@pytest.fixture(scope="session")
def test_db_engine():
    with PostgresContainer(
        "postgres:16-alpine",
        port=settings.POSTGRES_PORT,
        username=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        dbname=settings.POSTGRES_DB,
    ) as postgres:
        url = postgres.get_connection_url()
        engine = sqlalchemy.create_engine(url, echo=True)
        yield engine


@pytest.fixture(scope="session", autouse=True)
def initialize_db(test_db_engine):
    # TODO: Run migrations here once using Alembic
    BaseRecord.metadata.create_all(test_db_engine)


@pytest.fixture(scope="session")
def test_app(test_db_engine):
    app = create_app(test_db_engine)
    return app


@pytest.fixture(scope="function")
def test_client(test_app):
    with TestClient(test_app) as c:
        yield c


@pytest.fixture(scope="function")
def test_session_manager(test_db_engine):
    return DatabaseSessionManager(test_db_engine)


@pytest.fixture(scope="function")
def test_db_session(test_session_manager):
    """Fixture to provide a clean DB session per test function.

    This method yields a session and rolls it back after test completion
    so tests do not actually alter the DB state (which is initialized once per test suite).

    Reference: https://dev.to/jbrocher/fastapi-testing-a-database-5ao5
    """
    with test_session_manager.connect() as connection:
        try:
            session = Session(bind=connection)
            yield session
        finally:
            session.rollback()


@pytest.fixture(scope="function", autouse=True)
def session_override(test_app, test_db_session):
    def get_db_session_override():
        yield test_db_session[0]

    test_app.dependency_overrides[get_db_session] = get_db_session_override
