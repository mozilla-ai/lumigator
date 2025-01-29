from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, status
from lumigator_schemas.experiments import (
    ExperimentCreate,
    ExperimentIdCreate,
    ExperimentIdResponse,
    ExperimentResponse,
    ExperimentResultDownloadResponse,
    ExperimentResultResponse,
)
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    JobEvalCreate,
)

from backend.api.deps import ExperimentServiceDep, JobServiceDep
from backend.services.exceptions.base_exceptions import ServiceError
from backend.services.exceptions.experiment_exceptions import ExperimentNotFoundError

router = APIRouter()


def experiment_exception_mappings() -> dict[type[ServiceError], HTTPStatus]:
    return {
        ExperimentNotFoundError: status.HTTP_404_NOT_FOUND,
    }


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
# "new" routes
####################################################################################################
# These "experiments_new" routes are not yet ready to be exposed in the OpenAPI schema,
# because it is designed for the API when 'workflows' are supported
# TODO: Eventually this route will become the / route,
# but right now it is a placeholder while we build up the Workflows routes
# It's not included in the OpenAPI schema for now so it's not visible in the docs
@router.post("/new", status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_experiment_id(
    service: ExperimentServiceDep, request: ExperimentIdCreate
) -> ExperimentIdResponse:
    """Create an experiment ID."""
    return ExperimentResponse.model_validate(service.create_experiment(request).model_dump())


# TODO: FIXME this should not need the /all suffix.
# See further discussion https://github.com/mozilla-ai/lumigator/pull/728/files/2c960962c365d72e0714a16333884f0f209d214e#r1932176937
@router.get("/new/all", include_in_schema=False)
def list_experiments_new(
    service: ExperimentServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[ExperimentResponse]:
    """List all experiments."""
    return ListingResponse[ExperimentResponse].model_validate(
        service.list_experiments(skip, limit).model_dump()
    )


@router.get("/new/{experiment_id}", include_in_schema=False)
def get_experiment_new(service: ExperimentServiceDep, experiment_id: UUID) -> ExperimentResponse:
    """Get an experiment by ID."""
    return ExperimentResponse.model_validate(service.get_experiment(experiment_id).model_dump())


@router.get("/new/{experiment_id}/workflows", include_in_schema=False)
def get_workflows(service: ExperimentServiceDep, experiment_id: UUID) -> ListingResponse[UUID]:
    """TODO: this endpoint should handle passing in an experiment id and the returning a list
    of all the workflows associated with that experiment. Until workflows are stored and associated
    with experiments, this is not yet implemented.
    """
    raise NotImplementedError
