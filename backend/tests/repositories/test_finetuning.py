import pytest

from src.repositories.finetuning import FinetuningJobRepository


@pytest.fixture
def job_repository(test_db_session):
    return FinetuningJobRepository(test_db_session)


def test_create_and_get_job(job_repository):
    created_job = job_repository.create(name="test", submission_id="ray")
    retrieved_job = job_repository.get(created_job.id)
    assert created_job.id == retrieved_job.id
    assert created_job.name == retrieved_job.name
    assert created_job.submission_id == retrieved_job.submission_id


def test_list_jobs(job_repository):
    job_repository.create(name="job 1", submission_id="ray 1")
    job_repository.create(name="job 2", submission_id="ray 2")

    jobs = job_repository.list()
    assert len(jobs) == 2

    jobs = job_repository.list(skip=10)
    assert len(jobs) == 0


def test_job_count(job_repository):
    job_repository.create(name="job 1", submission_id="ray 1")
    job_repository.create(name="job 2", submission_id="ray 2")

    count = job_repository.count()
    assert count == 2
