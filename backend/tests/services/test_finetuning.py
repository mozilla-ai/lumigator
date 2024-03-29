import uuid

import pytest
from fastapi import HTTPException

from src.repositories.finetuning import FinetuningJobRepository
from src.schemas.finetuning import FinetuningJobUpdate
from tests.fakes.finetuning_service import FakeFinetuningService


@pytest.fixture
def finetuning_service(db_session):
    job_repo = FinetuningJobRepository(db_session)
    return FakeFinetuningService(job_repo)


def test_not_found_exception(finetuning_service):
    with pytest.raises(HTTPException, match="not found"):
        random_id = uuid.uuid4()
        finetuning_service.get_job(random_id)

    with pytest.raises(HTTPException, match="not found"):
        random_id = uuid.uuid4()
        finetuning_service.update_job(random_id, FinetuningJobUpdate())
