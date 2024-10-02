from backend.records.base import BaseRecord
from backend.records.mixins import DateTimeMixin, DeploymentStatusMixin, NameDescriptionMixin


class GroundTruthDeploymentRecord(
    BaseRecord, NameDescriptionMixin, DeploymentStatusMixin, DateTimeMixin
):
    __tablename__ = "groundtruth-deployments"
