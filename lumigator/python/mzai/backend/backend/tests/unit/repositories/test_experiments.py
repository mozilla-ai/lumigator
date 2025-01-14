import uuid

import pytest
from lumigator_schemas.jobs import JobStatus
from sqlalchemy.exc import IntegrityError

from backend.repositories.experiments import ExperimentRepository
from backend.repositories.jobs import JobRepository


@pytest.fixture
def experiment_repository(db_session):
    return ExperimentRepository(db_session)


@pytest.fixture
def job_repository(db_session):
    return JobRepository(db_session)


def test_create_and_get_experiment(experiment_repository):
    created_experiment = experiment_repository.create(name="test", description="")
    retrieved_experiment = experiment_repository.get(created_experiment.id)
    assert created_experiment.id == retrieved_experiment.id
    assert created_experiment.name == retrieved_experiment.name
    assert created_experiment.status == JobStatus.CREATED


def test_experiment_foreign_key(experiment_repository, job_repository):
    random_id = uuid.uuid4()
    experiment_repository.delete(random_id)
    with pytest.raises(IntegrityError):
        job_repository.create(name="test", description="", experiment_id=random_id)
