import uuid

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from mzai.backend.api.deps import DBSessionDep, get_finetuning_service
from mzai.backend.repositories.finetuning import FinetuningJobRepository
from mzai.backend.tests.fakes.finetuning_service import FakeFinetuningService
from mzai.schemas.extras import ListingResponse
from mzai.schemas.finetuning import (
    FinetuningJobCreate,
    FinetuningJobResponse,
    FinetuningJobUpdate,
)


@pytest.fixture
def create_jobs_via_backdoor(db_session):
    def create_func(n_jobs: int) -> list[uuid.UUID]:
        created_ids = []
        job_repo = FinetuningJobRepository(db_session)
        for i in range(n_jobs):
            record = job_repo.create(name=f"Job {i}", description="")
            created_ids.append(record.id)
        return created_ids

    return create_func


@pytest.fixture(scope="function", autouse=True)
def finetuning_service_override(app) -> None:
    """Override the FastAPI dependency injection with a fake finetuning service.

    Reference: https://fastapi.tiangolo.com/he/advanced/testing-database/
    """

    def get_finetuning_service_override(session: DBSessionDep):
        job_repo = FinetuningJobRepository(session)
        yield FakeFinetuningService(job_repo)

    app.dependency_overrides[get_finetuning_service] = get_finetuning_service_override


def test_create_job(client: TestClient):
    request = FinetuningJobCreate(name="job", description="fake", config={})
    response = client.post("/finetuning/jobs", json=request.model_dump())
    assert response.status_code == status.HTTP_201_CREATED


def test_get_job(client: TestClient, create_jobs_via_backdoor):
    created_id = create_jobs_via_backdoor(n_jobs=1)[0]

    response = client.get(f"/finetuning/jobs/{created_id}")
    assert response.status_code == status.HTTP_200_OK
    retrieved_job = FinetuningJobResponse.model_validate(response.json())
    assert retrieved_job.id == created_id


def test_get_missing_job(client: TestClient):
    random_id = uuid.uuid4()
    response = client.get(f"/finetuning/jobs/{random_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_jobs(client: TestClient, create_jobs_via_backdoor):
    # List on an empty database
    empty_response = client.get("/finetuning/jobs")
    assert empty_response.status_code == status.HTTP_200_OK
    empty_listing = ListingResponse.model_validate(empty_response.json())
    assert empty_listing.total == 0
    assert len(empty_listing.items) == 0

    # Create some jobs via repository backdoor
    n_jobs = 5
    create_jobs_via_backdoor(n_jobs=n_jobs)

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
    assert skip_listing.total == n_jobs
    assert len(skip_listing.items) == 2


def test_update_job(client: TestClient, create_jobs_via_backdoor):
    update_request = FinetuningJobUpdate(name="updated", description="updated")

    # Before job exists
    random_id = uuid.uuid4()
    response = client.put(f"/finetuning/jobs/{random_id}", json=update_request.model_dump())
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # After creating job
    created_id = create_jobs_via_backdoor(n_jobs=1)[0]
    response = client.put(f"/finetuning/jobs/{created_id}", json=update_request.model_dump())
    assert response.status_code == status.HTTP_200_OK
    updated_job = FinetuningJobResponse.model_validate(response.json())
    assert updated_job.name == update_request.name
    assert updated_job.description == update_request.description
