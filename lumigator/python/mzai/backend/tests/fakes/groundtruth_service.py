from mzai.backend.repositories.groundtruth import GroundTruthDeploymentRepository
from mzai.backend.services.groundtruth import GroundTruthService


class FakeRayServe:
    def deploy_applications(self, config: dict) -> dict:
        return {}


class FakeGroundTruthService(GroundTruthService):
    def __init__(
        self,
        deployment_repo: GroundTruthDeploymentRepository,
    ):
        self.deployment_repo = deployment_repo
        self.ray_client = None
