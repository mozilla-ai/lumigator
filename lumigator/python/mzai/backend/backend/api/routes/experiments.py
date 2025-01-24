from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, status
from lumigator_schemas.experiments import (
    ExperimentCreate,
    ExperimentIdCreate,
    ExperimentResponse,
    ExperimentResultDownloadResponse,
    ExperimentResultResponse,
)
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    JobEvalCreate,
)

from backend.api.deps import ExperimentServiceDep, JobServiceDep

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_experiment(
    service: JobServiceDep, request: ExperimentCreate, background_tasks: BackgroundTasks
) -> ExperimentResponse:
    return service.create_job(JobEvalCreate.model_validate(request.model_dump()), background_tasks)


@router.get("/{experiment_id}")
def get_experiment(service: JobServiceDep, experiment_id: UUID) -> ExperimentResponse:
    return ExperimentResponse.model_validate(service.get_job(experiment_id).model_dump())


@router.get("/")
def list_experiments(
    service: JobServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[ExperimentResponse]:
    return ListingResponse[ExperimentResponse].model_validate(
        service.list_jobs(skip, limit).model_dump()
    )


@router.get("/{experiment_id}/result")
def get_experiment_result(
    service: JobServiceDep,
    experiment_id: UUID,
) -> ExperimentResultResponse:
    """Return experiment results metadata if available in the DB."""
    return ExperimentResultResponse.model_validate(
        service.get_job_result(experiment_id).model_dump()
    )


@router.get("/{experiment_id}/result/download")
def get_experiment_result_download(
    service: JobServiceDep,
    experiment_id: UUID,
) -> ExperimentResultDownloadResponse:
    """Return experiment results file URL for downloading."""
    return ExperimentResultDownloadResponse.model_validate(
        service.get_job_result_download(experiment_id).model_dump()
    )


####################################################################################################
# V2 routes
####################################################################################################
# These routes are not yet ready to be exposed in the OpenAPI schema, because it is designed for the
# API when 'workflows' are supported
# TODO: Eventually this route will become the / route,
# but right now it is a placeholder while we build up the Workflows routes
# It's not included in the OpenAPI schema for now so it's not visible in the docs
@router.post("/v2", status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_experiment_id(
    service: ExperimentServiceDep, request: ExperimentIdCreate
) -> ExperimentResponse:
    """Create an experiment ID."""
    return service.create_experiment(request)


@router.get("/v2", include_in_schema=False)
def list_experiments_v2(
    service: ExperimentServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[ExperimentResponse]:
    """List all experiments."""
    return ListingResponse[ExperimentResponse].model_validate(
        service.list_experiments(skip, limit).model_dump()
    )


@router.get("/v2/{experiment_id}", include_in_schema=False)
def get_experiment_v2(service: ExperimentServiceDep, experiment_id: UUID) -> ExperimentResponse:
    """Get an experiment by ID."""
    return ExperimentResponse.model_validate(service.get_experiment(experiment_id).model_dump())


@router.get("/v2/{experiment_id}/jobs", include_in_schema=False)
def get_experiment_jobs(
    service: ExperimentServiceDep, experiment_id: UUID
) -> ListingResponse[UUID]:
    """Get all jobs associated with an experiment."""
    return service.get_all_owned_jobs(experiment_id)


@router.get("/v2/{experiment_id}/workflows", include_in_schema=False)
def get_workflows(service: ExperimentServiceDep, experiment_id: UUID) -> ListingResponse[UUID]:
    """TODO: this endpoint should handle passing in an experiment id and the returning a list
    of all the workflows associated with that experiment. Until workflows are stored and associated
    with experiments, this is not yet implemented.
    """
    raise NotImplementedError
