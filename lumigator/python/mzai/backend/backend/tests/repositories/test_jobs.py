import uuid
from math import exp

import pytest
from schemas.jobs import JobStatus
from sqlalchemy.exc import IntegrityError

from backend.repositories.jobs import JobRepository, JobResultRepository


@pytest.fixture
def job_repository(db_session):
    return JobRepository(db_session)


@pytest.fixture
def result_repository(db_session):
    return JobResultRepository(db_session)


def test_create_and_get_job(job_repository):
    created_job = job_repository.create(name="test", description="")
    retrieved_job = job_repository.get(created_job.id)
    assert created_job.id == retrieved_job.id
    assert created_job.name == retrieved_job.name
    assert created_job.status == JobStatus.CREATED


def test_job_foreign_key(result_repository):
    random_id = uuid.uuid4()
    with pytest.raises(IntegrityError):
        result_repository.create(job_id=random_id, metrics={})


def test_duplicate_results_error(job_repository, result_repository):
    job = job_repository.create(name="test", description="")
    result_repository.create(job_id=job.id, metrics={})
    with pytest.raises(IntegrityError):
        result_repository.create(job_id=job.id, metrics={})
