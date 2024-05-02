import pytest

from mzai.backend.repositories.finetuning import FinetuningJobRepository
from mzai.schemas.jobs import JobStatus


@pytest.fixture
def job_repository(db_session):
    return FinetuningJobRepository(db_session)


def test_create_and_get_job(job_repository):
    created_job = job_repository.create(name="test", description="")
    retrieved_job = job_repository.get(created_job.id)
    assert created_job.id == retrieved_job.id
    assert created_job.name == retrieved_job.name


def test_update_job(job_repository):
    job = job_repository.create(name="test", description="")
    job_repository.update(job.id, status=JobStatus.FAILED, description="Axolotl")
    job = job_repository.get(job.id)
    assert job.status == JobStatus.FAILED
    assert job.description == "Axolotl"


def test_list_jobs(job_repository):
    job_repository.create(name="job 1", description="")
    job_repository.create(name="job 2", description="")

    jobs = job_repository.list()
    assert len(jobs) == 2

    jobs = job_repository.list(skip=10)
    assert len(jobs) == 0


def test_job_count(job_repository):
    job_repository.create(name="job 1", description="")
    job_repository.create(name="job 2", description="")

    count = job_repository.count()
    assert count == 2
