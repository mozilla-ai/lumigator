from sqlalchemy.orm import Session

from mzai.backend.records.tasks import TaskRecord
from mzai.backend.repositories.base import BaseRepository


class TaskRepository(BaseRepository[TaskRecord]):
    def __init__(self, session: Session):
        super().__init__(TaskRecord, session)
