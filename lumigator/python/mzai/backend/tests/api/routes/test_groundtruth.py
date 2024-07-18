import uuid

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from mzai.backend.api.deps import DBSessionDep, get_ground_truth_service, GroundTruthServiceDep
from mzai.schemas.extras import ListingResponse
from mzai.schemas.groundtruth import (
    GroundTruthDeploymentCreate,
    GroundTruthDeploymentQueryResponse,
    GroundTruthDeploymentResponse,
    GroundTruthQueryRequest,
)
from mzai.backend.repositories.groundtruth import GroundTruthDeploymentRepository
from mzai.backend.tests.fakes.groundtruth_service import FakeGroundTruthService


@pytest.fixture(scope="function", autouse=True)
def groundtruth_service_override(app: FastAPI) -> None:
    """Override the FastAPI dependency injection with a fake groundtruth service.

    Reference: https://fastapi.tiangolo.com/he/advanced/testing-database/
    """

    def get_ground_truth_service_override(session: DBSessionDep):
        deployment_repo = GroundTruthDeploymentRepository(session)
        yield FakeGroundTruthService(deployment_repo)

    app.dependency_overrides[get_ground_truth_service] = get_ground_truth_service_override


def test_create_job(app_client: TestClient):
    request = GroundTruthDeploymentCreate(name="job", description="fake", config={})
    response = app_client.post("/deployments/", json=request.model_dump())
    assert response.status_code == status.HTTP_201_CREATED
