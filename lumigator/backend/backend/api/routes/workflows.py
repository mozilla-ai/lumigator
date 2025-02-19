from http import HTTPStatus

from fastapi import APIRouter, status
from lumigator_schemas.jobs import JobLogsResponse
from lumigator_schemas.workflows import (
    WorkflowCreateRequest,
    WorkflowDetailsResponse,
    WorkflowResponse,
)

from backend.api.deps import WorkflowServiceDep
from backend.services.exceptions.base_exceptions import ServiceError
from backend.services.exceptions.workflow_exceptions import (
    WorkflowNotFoundError,
    WorkflowValidationError,
)

router = APIRouter()


def workflow_exception_mappings() -> dict[type[ServiceError], HTTPStatus]:
    return {
        WorkflowNotFoundError: status.HTTP_404_NOT_FOUND,
        WorkflowValidationError: status.HTTP_400_BAD_REQUEST,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_workflow(service: WorkflowServiceDep, request: WorkflowCreateRequest) -> WorkflowResponse:
    """A workflow is a single execution for an experiment.
    A workflow is a collection of 1 or more jobs.
    It must be associated with an experiment id,
    which means you must already have created an experiment and have that ID in the request.
    """
    return WorkflowResponse.model_validate(service.create_workflow(request))


@router.get("/{workflow_id}")
def get_workflow(service: WorkflowServiceDep, workflow_id: str) -> WorkflowDetailsResponse:
    """Get a workflow by ID."""
    return WorkflowDetailsResponse.model_validate(service.get_workflow(workflow_id).model_dump())


# get the logs
@router.get("/{workflow_id}/logs")
def get_workflow_logs(service: WorkflowServiceDep, workflow_id: str) -> JobLogsResponse:
    """Get the logs for a workflow."""
    return JobLogsResponse.model_validate(service.get_workflow_logs(workflow_id).model_dump())


# delete a workflow
@router.delete("/{workflow_id}")
def delete_workflow(service: WorkflowServiceDep, workflow_id: str) -> WorkflowDetailsResponse:
    """Delete a workflow by ID."""
    return WorkflowDetailsResponse.model_validate(service.delete_workflow(workflow_id).model_dump())
