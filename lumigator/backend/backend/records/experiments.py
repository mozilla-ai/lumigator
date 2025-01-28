from backend.records.base import BaseRecord
from backend.records.mixins import DateTimeMixin, JobStatusMixin, NameDescriptionMixin


class ExperimentRecord(BaseRecord, NameDescriptionMixin, JobStatusMixin, DateTimeMixin):
    __tablename__ = "experiments"
