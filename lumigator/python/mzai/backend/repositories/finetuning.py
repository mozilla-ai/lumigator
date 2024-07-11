from sqlalchemy.orm import Session

from mzai.backend.records.finetuning import FinetuningJobRecord
from mzai.backend.repositories.base import BaseRepository


class FinetuningJobRepository(BaseRepository[FinetuningJobRecord]):
    def __init__(self, session: Session):
        super().__init__(FinetuningJobRecord, session)
