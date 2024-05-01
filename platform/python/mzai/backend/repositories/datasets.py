from sqlalchemy.orm import Session

from mzai.backend.records.datasets import DatasetRecord
from mzai.backend.repositories.base import BaseRepository


class DatasetRepository(BaseRepository[DatasetRecord]):
    def __init__(self, session: Session):
        super().__init__(DatasetRecord, session)
