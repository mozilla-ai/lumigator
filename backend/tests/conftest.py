from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from src.api.deps import get_db_session
from src.db import session_manager
from src.main import app


@pytest.fixture(scope="session")
def client(app) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    """Fixture to initialize the database once per test suite."""
    session_manager.initialize()
    yield
    session_manager.close()


@pytest.fixture(scope="function")
def db_session():
    """Fixture to provide a clean DB session per test function.

    This method yields a session and rolls it back after test completion
    so tests do not actually alter the DB state (which is initialized once per test suite).
    """
    with session_manager.session() as session:
        try:
            session.begin()  # Control when the outer transaction is started
            yield session
        finally:
            session.rollback()  # Roll back the outer transaction


@pytest.fixture(scope="function", autouse=True)
def session_override(db_session):
    def get_db_session_override():
        yield db_session[0]

    app.dependency_overrides[get_db_session] = get_db_session_override
