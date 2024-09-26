import uuid
from math import exp

import pytest
from schemas.jobs import JobStatus
from sqlalchemy.exc import IntegrityError

from app.repositories.experiments import ExperimentRepository, ExperimentResultRepository


@pytest.fixture
def experiment_repository(db_session):
    return ExperimentRepository(db_session)


@pytest.fixture
def result_repository(db_session):
    return ExperimentResultRepository(db_session)


def test_create_and_get_experiment(experiment_repository):
    created_experiment = experiment_repository.create(name="test", description="")
    retrieved_experiment = experiment_repository.get(created_experiment.id)
    assert created_experiment.id == retrieved_experiment.id
    assert created_experiment.name == retrieved_experiment.name
    assert created_experiment.status == JobStatus.CREATED


def test_experiment_foreign_key(result_repository):
    random_id = uuid.uuid4()
    with pytest.raises(IntegrityError):
        result_repository.create(experiment_id=random_id, metrics={})


def test_duplicate_results_error(experiment_repository, result_repository):
    experiment = experiment_repository.create(name="test", description="")
    result_repository.create(experiment_id=experiment.id, metrics={})
    with pytest.raises(IntegrityError):
        result_repository.create(experiment_id=experiment.id, metrics={})
