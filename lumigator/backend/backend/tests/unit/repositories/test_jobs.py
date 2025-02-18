import uuid
from math import exp

import pytest
from lumigator_schemas.jobs import JobStatus, JobType
from sqlalchemy.exc import IntegrityError

from backend.records.jobs import JobRecord
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


def test_create_and_get_jobs_per_type(job_repository):
    created_job = job_repository.create(name="test", description="")
    retrieved_job = job_repository.get(created_job.id)
    created_infer_job = job_repository.create(name="test", description="", job_type=JobType.INFERENCE.value)
    retrieved_infer_job = job_repository.list(
        skip=0, limit=None, criteria=[JobRecord.job_type == JobType.INFERENCE.value]
    )
    assert job_repository.count() == 2
    assert retrieved_job.job_type is None
    assert len(retrieved_infer_job) == 1
    assert created_infer_job.id == retrieved_infer_job[0].id
    assert created_infer_job.name == retrieved_infer_job[0].name
    assert created_infer_job.job_type == JobType.INFERENCE.value
    assert created_infer_job.status == JobStatus.CREATED


def test_job_foreign_key(result_repository):
    random_id = uuid.uuid4()
    with pytest.raises(IntegrityError):
        result_repository.create(job_id=random_id, metrics={})


def test_duplicate_results_error(job_repository, result_repository):
    job = job_repository.create(name="test", description="")
    result_repository.create(job_id=job.id, metrics={})
    with pytest.raises(IntegrityError):
        result_repository.create(job_id=job.id, metrics={})
