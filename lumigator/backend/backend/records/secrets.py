from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped

from backend.records.base import BaseRecord
from backend.records.mixins import CreatedAtMixin


class SecretRecord(BaseRecord, CreatedAtMixin):
    __tablename__ = "secrets"

    _name = Column("name", String, unique=True, index=True, nullable=False)
    value: Mapped[str]
    description: Mapped[str]

    @property
    def name(self):
        return self._name.lower()

    @name.setter
    def name(self, value):
        self._name = value.lower()

    def __init__(self, name: str, value: str, description: str = ""):
        super().__init__()
        self.name = name
        self.value = value
        self.description = description
