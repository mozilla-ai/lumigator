from pathlib import Path
from uuid import UUID
from http import HTTPMethod
from json import dumps

from schemas.groundtruth import GroundTruthDeploymentCreate, GroundTruthDeploymentResponse
from schemas.extras import ListingResponse

from client import ApiClient


class Deployments:
    DEPLOYMENTS_ROUTE = "deployments"

    def __init__(self, c: ApiClient):
        self.client = c

    def create_deployment(
        self, deployment: GroundTruthDeploymentCreate
    ) -> GroundTruthDeploymentResponse:
        """Creates a new groundtruth deployment."""
        response = (
            self.client.get_response(f"{self.EXPERIMENTS_ROUTE}"),
            HTTPMethod.POST,
            dumps(deployment),
        )

        if not response:
            return []

        data = response.json()
        return GroundTruthDeploymentResponse(**data)

    #     def get_deployment(self, deployment_id: UUID) -> GroundTruthDeploymentResponse:
    #         """Returns information on the deployment for the specified ID."""
    #         UUID(deployment_id)
    #         response = self.client.get_response(f'{self.EXPERIMENTS_ROUTE}/{deployment_id}')
    #
    #         if not response:
    #             return []
    #
    #         data = response.json()
    #         return GroundTruthDeploymentResponse(**data)

    def delete_deployment(self, deployment_id: UUID) -> GroundTruthDeploymentResponse:
        """Returns information on the deployment for the specified ID."""
        UUID(deployment_id)
        response = self.client.get_response(
            f"{self.EXPERIMENTS_ROUTE}/{deployment_id}", HTTPMethod.DELETE
        )

        if not response:
            return []

        data = response.json()
        return GroundTruthDeploymentResponse(**data)

    def get_deployments(
        self, skip: int = 0, limit: int = 100
    ) -> ListingResponse[GroundTruthDeploymentResponse]:
        """Returns information on all deployments."""
        response = self.client.get_response(f"{self.EXPERIMENTS_ROUTE}")

        if not response:
            return []

        return [GroundTruthDeploymentResponse(**args) for args in response.json()]
