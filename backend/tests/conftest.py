from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api.deps import get_db_session
from src.db import session_manager
from src.main import app


@pytest.fixture(scope="function")
def test_client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module", autouse=True)
def initialize_database():
    """Fixture to initialize the database once per test suite."""
    # TODO: Change this to run migrations once using Alembic
    session_manager.initialize()


@pytest.fixture(scope="function")
def db_session():
    """Fixture to provide a clean DB session per test function.

    This method yields a session and rolls it back after test completion
    so tests do not actually alter the DB state (which is initialized once per test suite).

    Reference: https://dev.to/jbrocher/fastapi-testing-a-database-5ao5
    """
    with session_manager.connect() as connection:
        try:
            session = Session(bind=connection)
            yield session
        finally:
            session.rollback()


@pytest.fixture(scope="function", autouse=True)
def session_override(db_session):
    def get_db_session_override():
        yield db_session[0]

    app.dependency_overrides[get_db_session] = get_db_session_override
