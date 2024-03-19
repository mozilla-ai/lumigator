from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from src.server import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c
