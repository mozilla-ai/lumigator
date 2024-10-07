from pathlib import Path
from uuid import UUID

from mzai.backend.schemas.datasets import DatasetResponse, DatasetResponseList
from mzai.backend.schemas.deployments import (
    DeploymentEvent,
    DeploymentEventList,
    DeploymentStatus,
    DeploymentType,
)

from mzai.backend.schemas.extras import ListingResponse

from sdk.client import ApiClient


class Deployments:
    DEPLOYMENTS_ROUTE = "Deployments"

    def __init__(self, c: ApiClient):
        self.client = c

    def create_deployment(self, Deployment: DeploymentCreate) -> DeploymentResponse:
        """Creates a new Deployment."""
        response = self.__post_response(str(Path(self.client._api_url) / self.DEPLOYMENTS_ROUTE / ''), Deployment.model_dump_json())

        if not response:
            return []

        data = response.json()
        return DeploymentResponse(**data)

    def get_deployment(self, Deployment_id: UUID) -> DeploymentResponse:
        """Returns information on the Deployment for the specified ID."""
        response = self.__get_response(str(Path(self._api_url) / self.DEPLOYMENTS_ROUTE))

        if not response:
            return []

        data = response.json()
        return DeploymentResponse(**data)

    def get_deployments(self, skip: int = 0, limit: int = 100) -> ListingResponse[DeploymentResponse]:
        """Returns information on all Deployments."""
        response = self.__get_response(str(Path(self._api_url) / self.DEPLOYMENTS_ROUTE))

        if not response:
            return []

        return [DeploymentResponse(**args) for args in response.json()]

    def get_deployment_result(self, Deployment_id: UUID) -> DeploymentResultResponse:
        """Returns the result of the Deployment for the specified ID."""
        response = self.client.__get_response(str(Path(self._api_url) / self.DEPLOYMENTS_ROUTE / f'{Deployment_id}' / "result"))

        if not response:
            return []

        data = response.json()
        return DeploymentResultResponse(**data)

    def get_Deployment_result_download(self, Deployment_id: UUID) -> DeploymentResultDownloadResponse:
        """Returns the result of the Deployment for the specified ID."""
        response = self.__get_response(
            str(Path(self.client._api_url) / self.DEPLOYMENTS_ROUTE / f'{Deployment_id}' / "result" / "download"))

        if not response:
            return []

        data = response.json()
        return DeploymentResultDownloadResponse(**data)