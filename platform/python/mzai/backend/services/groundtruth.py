from ray.dashboard.modules.serve.sdk import ServeSubmissionClient

from mzai.backend.api.deployments.summarizer_config_loader import SummarizerConfigLoader
from mzai.backend.repositories.groundtruth import GroundTruthDeploymentRepository
from mzai.schemas.extras import ListingResponse
from mzai.schemas.groundtruth import (
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

    def create_deployment(self):
        conf = SummarizerConfigLoader()
        deployment_args = conf.get_config_dict()
        deployment_name = conf.get_deployment_name()
        deployment_description = conf.get_deployment_description()

        self.ray_client.deploy_applications(deployment_args)

        record = self.deployment_repo.create(
            name=deployment_name, description=deployment_description
        )

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
