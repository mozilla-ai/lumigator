from sqlalchemy.orm import Mapped, mapped_column

from backend.records.base import BaseRecord
from backend.records.mixins import CreatedAtMixin


class SecretRecord(BaseRecord, CreatedAtMixin):
    __tablename__ = "secrets"
    name: Mapped[str] = mapped_column(unique=True)
    value: Mapped[str]
    description: Mapped[str]
