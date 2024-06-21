from mzai.schemas.extras import ListingResponse
from ray.dashboard.modules.serve.sdk import ServeSubmissionClient
from mzai.backend.repositories.groundtruth import GroundTruthDeploymentRepository
from mzai.schemas.groundtruth import (
    GroundTruthDeploymentCreate,
    GroundTruthDeploymentResponse,
    GroundTruthDeploymentUpdate,
    GroundTruthDeploymentLogsResponse,
)

class GroundTruthService:

    def __init__(self, deployment_repo: GroundTruthDeploymentRepository, ray_serve_client:ServeSubmissionClient):
        self.job_repo = deployment_repo
        self.ray_client = ray_serve_client

    def create_deployment(self):
        pass

    def list_deployments(self, skip: int = 0, limit: int = 100) -> ListingResponse[GroundTruthDeploymentResponse]:
        total = self.job_deployment.count()
        records = self.job_deployment.list(skip, limit)
        return ListingResponse(
            total=total,
            items=[GroundTruthDeploymentResponse.model_validate(x) for x in records],
        )

