from mzai.schemas.extras import ListingResponse
from mzai.schemas.groundtruth import (
    GroundTruthDeploymentCreate,
    GroundTruthDeploymentResponse,
    GroundTruthDeploymentUpdate,
    GroundTruthDeploymentLogsResponse,
)

class GroundTruthService:

    def create_deployment(self):
        pass

    def list_deployments(self, skip: int = 0, limit: int = 100) -> ListingResponse[GroundTruthDeploymentResponse]:
        total = self.job_repo.count()
        records = self.job_repo.list(skip, limit)
        return ListingResponse(
            total=total,
            items=[GroundTruthDeploymentResponse.model_validate(x) for x in records],
        )

