from sqlalchemy.orm import Mapped, mapped_column

from backend.records.base import BaseRecord
from backend.records.mixins import CreatedAtMixin


class KeyRecord(BaseRecord, CreatedAtMixin):
    __tablename__ = "keys"
    key_name: Mapped[str] = mapped_column(unique=True)
    key_value: Mapped[str]
    description: Mapped[str]
