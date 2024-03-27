import uuid

import pytest
from fastapi.testclient import TestClient

from src.repositories.finetuning import FinetuningJobRepository
from src.schemas.extras import ListingResponse


@pytest.fixture
def create_jobs_via_backdoor(db_session):
    def create(n_jobs: int):
        job_repo = FinetuningJobRepository(db_session)
        for i in range(n_jobs):
            job_repo.create(name=f"Job {i}", submission_id=f"Ray {i}")

    return create


def test_get_unknown_job(client: TestClient):
    random_uid = uuid.uuid4()
    response = client.get(f"finetuning/jobs/{random_uid}")
    assert response.status_code == 404


def test_list_jobs(client: TestClient, create_jobs_via_backdoor):
    # List on an empty database
    empty_response = client.get("finetuning/jobs")
    assert empty_response.status_code == 200
    empty_listing = ListingResponse.model_validate(empty_response.json())
    assert empty_listing.total == 0
    assert len(empty_listing.items) == 0

    # Create some jobs via repository backdoor
    create_jobs_via_backdoor(n_jobs=5)

    # Check listing after jobs created
    five_response = client.get("finetuning/jobs")
    assert five_response.status_code == 200
    five_listing = ListingResponse.model_validate(five_response.json())
    assert five_listing.total == 5
    assert len(five_listing.items) == 5

    # Check listing with skip and limit
    skip_response = client.get("finetuning/jobs?skip=2&limit=2")
    assert skip_response.status_code == 200
    skip_listing = ListingResponse.model_validate(skip_response.json())
    assert skip_listing.total == 5
    assert len(skip_listing.items) == 2
