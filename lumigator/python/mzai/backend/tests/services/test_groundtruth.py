import pytest

from mzai.backend.api.routes import groundtruth
from mzai.backend.repositories.groundtruth import GroundTruthDeploymentRepository
from mzai.backend.tests.fakes.groundtruth_service import FakeGroundTruthService
from mzai.schemas.extras import ListingResponse


@pytest.fixture
def groundtruth_service(db_session):
    job_repo = GroundTruthDeploymentRepository(db_session)
    return FakeGroundTruthService(job_repo)


def test_create_empty_service(groundtruth_service: FakeGroundTruthService):
    results = groundtruth.list_groundtruth_deployments(groundtruth_service)
    assert results.total == 0
    assert results.items == []
    assert isinstance(results, ListingResponse)
