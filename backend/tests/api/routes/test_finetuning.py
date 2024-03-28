import uuid

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from src.repositories.finetuning import FinetuningJobRepository
from src.schemas.extras import ListingResponse
from src.schemas.finetuning import FinetuningJobResponse


@pytest.fixture
def create_jobs_via_backdoor_func(db_session):
    def create(n_jobs: int):
        created_ids = []
        job_repo = FinetuningJobRepository(db_session)
        for i in range(n_jobs):
            record = job_repo.create(name=f"Job {i}", submission_id=f"Ray {i}")
            created_ids.append(record.id)
        return created_ids

    return create


# TODO: This will actually trigger the Ray job, perhaps mock this out somehow
#       Do we want to be using a real Ray cluster in these ITs, or fake out the interactions?
# def test_create_job(client: TestClient):
#     # Create via API route
#
#     request = FinetuningJobCreate(name="test-job", config={})
#     response = client.post("/finetuning/jobs", json=request.model_dump())
#     assert response.status_code == status.HTTP_201_CREATED


def test_get_job(client: TestClient, create_jobs_via_backdoor_func):
    created_id = create_jobs_via_backdoor_func(n_jobs=1)[0]

    response = client.get(f"/finetuning/jobs/{created_id}")
    assert response.status_code == status.HTTP_200_OK
    retrieved_job = FinetuningJobResponse.model_validate(response.json())
    assert retrieved_job.id == created_id


def test_get_missing_job(client: TestClient):
    random_id = uuid.uuid4()
    response = client.get(f"/finetuning/jobs/{random_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_jobs(client: TestClient, create_jobs_via_backdoor_func):
    # List on an empty database
    empty_response = client.get("/finetuning/jobs")
    assert empty_response.status_code == status.HTTP_200_OK
    empty_listing = ListingResponse.model_validate(empty_response.json())
    assert empty_listing.total == 0
    assert len(empty_listing.items) == 0

    # Create some jobs via repository backdoor
    n_jobs = 5
    create_jobs_via_backdoor_func(n_jobs=n_jobs)

    # Check listing after jobs created
    all_response = client.get("/finetuning/jobs")
    assert all_response.status_code == status.HTTP_200_OK
    all_listing = ListingResponse.model_validate(all_response.json())
    assert all_listing.total == n_jobs
    assert len(all_listing.items) == n_jobs

    # Check listing with skip and limit
    skip_response = client.get("/finetuning/jobs?skip=2&limit=2")
    assert skip_response.status_code == status.HTTP_200_OK
    skip_listing = ListingResponse.model_validate(skip_response.json())
    assert skip_listing.total == 5
    assert len(skip_listing.items) == 2
