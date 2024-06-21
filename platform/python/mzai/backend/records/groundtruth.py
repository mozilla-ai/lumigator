from mzai.backend.records.base import BaseRecord
from mzai.backend.records.mixins import NameDescriptionMixin, DeploymentStatusMixin, DateTimeMixin


class GroundTruthDeploymentRecord(
    BaseRecord, NameDescriptionMixin, DeploymentStatusMixin, DateTimeMixin
):
    __tablename__ = "groundtruth-deployments"
