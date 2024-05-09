from mzai.backend.records.base import BaseRecord
from mzai.backend.records.mixins import DateTimeMixin, JobStatusMixin, NameDescriptionMixin


class FinetuningJobRecord(BaseRecord, NameDescriptionMixin, JobStatusMixin, DateTimeMixin):
    __tablename__ = "finetuning-jobs"
