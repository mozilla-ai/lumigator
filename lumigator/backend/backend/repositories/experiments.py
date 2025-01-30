from sqlalchemy.orm import Session

from backend.records.experiments import ExperimentRecord
from backend.repositories.base import BaseRepository


class ExperimentRepository(BaseRepository[ExperimentRecord]):
    def __init__(self, session: Session):
        super().__init__(ExperimentRecord, session)
