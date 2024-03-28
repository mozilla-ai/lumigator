import uuid

import pytest
from fastapi import HTTPException

from src.repositories.finetuning import FinetuningJobRepository
from tests.fakes.finetuning_service import FakeFinetuningService


@pytest.fixture
def finetuning_service(db_session):
    job_repo = FinetuningJobRepository(db_session)
    return FakeFinetuningService(job_repo)


def test_get_missing_job_raises(finetuning_service):
    with pytest.raises(HTTPException, match="not found"):
        finetuning_service.get_job(uuid.uuid4())
