from app.records.base import BaseRecord
from app.records.mixins import DateTimeMixin, DeploymentStatusMixin, NameDescriptionMixin


class GroundTruthDeploymentRecord(
    BaseRecord, NameDescriptionMixin, DeploymentStatusMixin, DateTimeMixin
):
    __tablename__ = "groundtruth-deployments"
