"""These are the runs routes.
A run is a single execution of an experiment, which can be a single job or a batch of jobs.
"""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, status
from lumigator_schemas.workflows import (
    WorkflowCreate,
    WorkflowDetailsResponse,
    WorkflowResponse,
    WorkflowSummaryResponse,
)

from backend.api.deps import WorkflowServiceDep

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_workflow(
    service: WorkflowServiceDep, request: WorkflowCreate, background_tasks: BackgroundTasks
) -> WorkflowResponse:
    """A workflow is a single execution of an experiment,
    which can be a single job or a collection of jobs. It must be associated with an experiment id
    (which means you must already have created an experiment and have that ID in the request).
    """
    return WorkflowResponse.model_validate(service.create_workflow(request, background_tasks))


@router.get("/{workflow_id}")
def get_workflow(service: WorkflowServiceDep, workflow_id: UUID) -> WorkflowResponse:
    """TODO: The workflow meta is currently not saved in the database so it can't be retrieved
    In order to get all the info about a workflow
    you need to get all the workflows for an experiment.
    This means you can't yet compile a list of all workflows for an experiment, work in progress.
    """
    raise NotImplementedError


@router.get("/{workflow_id}/summary")
def get_workflow_summary(
    service: WorkflowServiceDep,
    workflow_id: UUID,
) -> WorkflowSummaryResponse:
    """TODO:Return the results metadata for a run if available in the DB.
    This should retrieve the metadata for the job or jobs that were run in the workflow and compile
    them into a single response that can be used to populate the UI.
    Currently this looks like taking the avg results for the
    inference job (tok/s, gen length, etc) and the
    average results for the evaluation job (ROUGE, BLEU, etc) and
    returning them in a single response.
    For detailed results you would want to ping the get_workflow_details endpoint.
    """
    raise NotImplementedError


@router.get("/{workflow_id}/result/download")
def get_workflow_details(
    service: WorkflowServiceDep,
    workflow_id: UUID,
) -> WorkflowDetailsResponse:
    """TODO: Retrieve the detailed results for a specific workflow.
    This endpoint fetches the detailed results of the jobs that
    were run as part of the specified workflow. Unlike the get_workflow_summary endpoint,
    this endpoint returns the raw results of the jobs (stats for each example in the dataset).
    It compiles the results into a downloadable format,
    which can be used for further analysis or record-keeping.
    """
    raise NotImplementedError
