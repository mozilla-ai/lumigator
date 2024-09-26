from sqlalchemy.orm import Session

from app.records.datasets import DatasetRecord
from app.repositories.base import BaseRepository


class DatasetRepository(BaseRepository[DatasetRecord]):
    def __init__(self, session: Session):
        super().__init__(DatasetRecord, session)
