
from sqlalchemy.orm import Session

from backend.records.keys import KeyRecord
from backend.repositories.base import BaseRepository


class KeyRepository(BaseRepository[KeyRecord]):
    def __init__(self, session: Session):
        super().__init__(KeyRecord, session)

    def get_by_key_name(self, key_name: str) -> KeyRecord | None:
        return self.session.query(KeyRecord).where(KeyRecord.key_name == key_name).all().first()
