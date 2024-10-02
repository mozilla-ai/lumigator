from backend.services.groundtruth import GroundTruthService
from backend.repositories.groundtruth import GroundTruthDeploymentRepository


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
