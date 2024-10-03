from sqlalchemy.orm import Session

from backend.records.datasets import DatasetRecord
from backend.repositories.base import BaseRepository


class DatasetRepository(BaseRepository[DatasetRecord]):
    def __init__(self, session: Session):
        super().__init__(DatasetRecord, session)
