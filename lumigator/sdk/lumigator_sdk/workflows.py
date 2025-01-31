from http import HTTPMethod

from lumigator_schemas.jobs import JobLogsResponse
from lumigator_schemas.workflows import (
    WorkflowCreateRequest,
    WorkflowDetailsResponse,
    WorkflowResponse,
)

from lumigator_sdk.client import ApiClient
from lumigator_sdk.strict_schemas import WorkflowCreateRequest as WorkflowCreateRequestStrict


class Workflows:
    WORKFLOWS_ROUTE = "workflows"

    def __init__(self, c: ApiClient):
        self.__client = c

    def create_workflow(self, workflow: WorkflowCreateRequest) -> WorkflowResponse:
        """Creates a new experiment."""
        WorkflowCreateRequestStrict.model_validate(WorkflowCreateRequest.model_dump(workflow))
        response = self.__client.get_response(
            self.WORKFLOWS_ROUTE, HTTPMethod.POST, workflow.model_dump_json()
        )

        data = response.json()
        return WorkflowResponse(**data)

    def get_workflow(self, workflow_id: str) -> WorkflowDetailsResponse | None:
        """Returns information on the experiment for the specified ID."""
        response = self.__client.get_response(f"{self.WORKFLOWS_ROUTE}/{workflow_id}")

        data = response.json()
        return WorkflowDetailsResponse(**data)

    def get_workflow_logs(self, workflow_id: str) -> JobLogsResponse | None:
        """Returns information on the experiment for the specified ID."""
        response = self.__client.get_response(f"{self.WORKFLOWS_ROUTE}/{workflow_id}/logs")

        data = response.json()
        return JobLogsResponse(**data)

    def delete_workflow(self, workflow_id: str) -> None:
        """Deletes the experiment for the specified ID."""
        self.__client.get_response(f"{self.WORKFLOWS_ROUTE}/{workflow_id}", HTTPMethod.DELETE)
        return None
