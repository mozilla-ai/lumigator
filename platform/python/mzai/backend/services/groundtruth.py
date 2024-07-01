from ray.dashboard.modules.serve.sdk import ServeSubmissionClient

from mzai.backend.api.deployments.configloader import ConfigLoader
from mzai.backend.repositories.groundtruth import GroundTruthDeploymentRepository
from mzai.schemas.deployments import DeploymentConfig, DeploymentType
from mzai.schemas.extras import ListingResponse
from mzai.schemas.groundtruth import (
    GroundTruthDeploymentCreate,
    GroundTruthDeploymentResponse,
)


class GroundTruthService:
    def __init__(
        self,
        deployment_repo: GroundTruthDeploymentRepository,
        ray_serve_client: ServeSubmissionClient,
    ):
        self.deployment_repo = deployment_repo
        self.ray_client = ray_serve_client

    def create_deployment(self, request: GroundTruthDeploymentCreate):
        record = self.deployment_repo.create(name=request.name, description=request.description)
        deployment_args = ConfigLoader("deployments/summarizer.yaml").read_config()
        config = DeploymentConfig(
            deployment_type=DeploymentType.GROUNDTRUTH,
            args=deployment_args,
        ).dict()
        self.ray_client.deploy_applications(config["args"])

        return GroundTruthDeploymentResponse.model_validate(record)

    def list_deployments(
        self, skip: int = 0, limit: int = 100
    ) -> (ListingResponse)[GroundTruthDeploymentResponse]:
        total = self.deployment_repo.count()
        records = self.deployment_repo.list(skip, limit)
        return ListingResponse(
            total=total,
            items=[GroundTruthDeploymentResponse.model_validate(x) for x in records],
        )
