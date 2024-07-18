import uuid

import pytest
from fastapi import HTTPException

from mzai.backend.repositories.groundtruth import GroundTruthDeploymentRepository
from mzai.backend.tests.fakes.groundtruth_service import FakeGroundTruthService, FakeRayServe
from mzai.schemas.extras import ListingResponse
from mzai.schemas.groundtruth import GroundTruthDeploymentResponse


@pytest.fixture
def groundtruth_service(db_session):
    job_repo = GroundTruthDeploymentRepository(db_session)
    return FakeGroundTruthService(job_repo)


def test_empty_servie(groundtruth_service: FakeGroundTruthService):
    results = groundtruth_service.list_deployments()
    assert results.total == 0
    assert results.items == []
    assert isinstance(results, ListingResponse)
