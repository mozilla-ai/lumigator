import uuid

import pytest
from backend.repositories.finetuning import FinetuningJobRepository
from fakes import FakeFinetuningService
from fastapi import HTTPException

from mzai.backend.schemas.finetuning import FinetuningJobUpdate


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
