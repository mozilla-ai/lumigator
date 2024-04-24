from sqlalchemy.orm import Session

from mzai.backend.records.finetuning import FinetuningJobRecord
from mzai.backend.repositories.base import BaseRepository


class FinetuningJobRepository(BaseRepository[FinetuningJobRecord]):
    def __init__(self, session: Session):
        super().__init__(FinetuningJobRecord, session)

    def create(self, name: str, description: str, submission_id: str) -> FinetuningJobRecord:
        job = FinetuningJobRecord(name=name, description=description, submission_id=submission_id)
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job
