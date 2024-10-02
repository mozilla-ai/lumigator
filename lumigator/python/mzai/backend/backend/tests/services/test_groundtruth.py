import pytest


from backend.repositories.groundtruth import (
    GroundTruthDeploymentRepository,
    GroundTruthDeploymentRecord,
)
from backend.tests.fakes.groundtruth_service import FakeGroundTruthService
from schemas.extras import ListingResponse
from backend.api.routes import groundtruth


@pytest.fixture
def groundtruth_service(db_session):
    deployment_repo = GroundTruthDeploymentRepository(db_session)
    return FakeGroundTruthService(deployment_repo)


def test_create_empty_service(groundtruth_service: FakeGroundTruthService):
    results = groundtruth.list_groundtruth_deployments(groundtruth_service)
    assert results.total == 0
    assert results.items == []
    assert isinstance(results, ListingResponse)


def test_delete_service(groundtruth_service: FakeGroundTruthService, db_session):
    # Get all deployment IDs from database in test session
    deployments = db_session.query(GroundTruthDeploymentRecord).all()
    # Delete all created deployments
    for val in deployments:
        results = groundtruth.delete_deployment(groundtruth_service, val)
        assert results == f"{val} deleted"
