from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, status
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import JobResponse
from lumigator_schemas.workflows import (
    WorkflowCreate,
    WorkflowDetailsResponse,
    WorkflowResponse,
    WorkflowResultDownloadResponse,
)

from backend.api.deps import WorkflowServiceDep

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_workflow(
    service: WorkflowServiceDep, request: WorkflowCreate, background_tasks: BackgroundTasks
) -> WorkflowResponse:
    """A workflow is a single execution for an experiment.
    A workflow is a collection of 1 or more jobs.
    It must be associated with an experiment id,
    which means you must already have created an experiment and have that ID in the request.
    """
    return WorkflowResponse.model_validate(service.create_workflow(request, background_tasks))


@router.get("/{workflow_id}")
def get_workflow(service: WorkflowServiceDep, workflow_id: UUID) -> WorkflowResponse:
    """TODO: The workflow objects are currently not saved in the database so it can't be retrieved.
    In order to get all the info about a workflow,
    you need to get all the jobs for an experiment and make some decisions about how to use them.
    This means you can't yet easily compile a list of all workflows for an experiment.
    """
    raise NotImplementedError


# TODO: currently experiment_id=workflow_id, but this will change
@router.get("/{experiment_id}/jobs", include_in_schema=False)
def get_workflow_jobs(
    service: WorkflowServiceDep, experiment_id: UUID
) -> ListingResponse[JobResponse]:
    """Get all jobs for a workflow.
    TODO: this will likely eventually be merged with the get_workflow endpoint, once implemented
    """
    # TODO right now this command expects that the workflow_id is the same as the experiment_id
    return ListingResponse[JobResponse].model_validate(
        service.get_workflow_jobs(experiment_id).model_dump()
    )


@router.get("/{workflow_id}/details")
def get_workflow_details(
    service: WorkflowServiceDep,
    workflow_id: UUID,
) -> WorkflowDetailsResponse:
    """TODO:Return the results metadata for a run if available in the DB.
    This should retrieve the metadata for the job or jobs that were run in the workflow and compile
    them into a single response that can be used to populate the UI.
    Currently this looks like taking the average results for the
    inference job (tok/s, gen length, etc) and the
    average results for the evaluation job (ROUGE, BLEU, etc) and
    returning them in a single response.
    For detailed results you would want to use the get_workflow_details endpoint.
    """
    raise NotImplementedError


@router.get("/{workflow_id}/details")
def get_experiment_result_download(
    service: WorkflowServiceDep,
    workflow_id: UUID,
) -> WorkflowResultDownloadResponse:
    """Return experiment results file URL for downloading."""
    return WorkflowResultDownloadResponse.model_validate(
        service.get_workflow_result_download(workflow_id).model_dump()
    )
