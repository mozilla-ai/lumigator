from sqlalchemy.orm import Session

from backend.records.secrets import SecretRecord
from backend.repositories.base import BaseRepository


class SecretRepository(BaseRepository[SecretRecord]):
    def __init__(self, session: Session):
        super().__init__(SecretRecord, session)

    def get_secret_by_name(self, name: str) -> SecretRecord | None:
        return self.session.query(SecretRecord).where(SecretRecord.name == name).first()
