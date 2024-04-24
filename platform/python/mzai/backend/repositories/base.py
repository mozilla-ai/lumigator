from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

from mzai.backend.db import BaseRecord

RecordType = TypeVar("RecordType", bound=BaseRecord)


class BaseRepository(Generic[RecordType]):
    def __init__(self, record_cls: type[RecordType], session: Session):
        self.record_cls = record_cls
        self.session = session

    def count(self) -> int:
        return self.session.query(self.record_cls).count()

    def create(self, **fields) -> RecordType:
        record = self.record_cls(**fields)
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def update(self, record_id: UUID, **updates) -> RecordType | None:
        record = self.get(record_id)
        if record is None:
            return None
        for key, value in updates.items():
            setattr(record, key, value)
        self.session.commit()
        self.session.refresh(record)
        return record

    def get(self, record_id: UUID) -> RecordType | None:
        return self.session.get(self.record_cls, record_id)

    def list(self, skip: int = 0, limit: int = 100) -> list[RecordType]:
        return self.session.query(self.record_cls).offset(skip).limit(limit).all()
