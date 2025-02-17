from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, status
from lumigator_schemas.experiments import (
    ExperimentCreate,
    ExperimentIdCreate,
    GetExperimentResponse,
)
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    JobCreate,
    JobResponse,
    JobResultDownloadResponse,
    JobResultResponse,
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
    service: JobServiceDep,
    request: ExperimentCreate,
) -> GetExperimentResponse:
    return service.create_job(JobCreate.model_validate(request.model_dump()))


@router.get("/{experiment_id}")
def get_experiment(service: JobServiceDep, experiment_id: UUID) -> JobResponse:
    return GetExperimentResponse.model_validate(service.get_job(experiment_id).model_dump())


@router.get("/")
def list_experiments(
    service: JobServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[JobResponse]:
    return ListingResponse[JobResponse].model_validate(service.list_jobs(skip, limit).model_dump())


@router.get("/{experiment_id}/result")
def get_experiment_result(
    service: JobServiceDep,
    experiment_id: UUID,
) -> JobResultResponse:
    """Return experiment results metadata if available in the DB."""
    return JobResultResponse.model_validate(service.get_job_result(experiment_id).model_dump())


@router.get("/{experiment_id}/result/download")
def get_experiment_result_download(
    service: JobServiceDep,
    experiment_id: UUID,
) -> JobResultDownloadResponse:
    """Return experiment results file URL for downloading."""
    return JobResultDownloadResponse.model_validate(service.get_job_result_download(experiment_id).model_dump())


####################################################################################################
# "new" routes
####################################################################################################
# These "experiments_new" routes are not yet ready to be exposed in the OpenAPI schema,
# because it is designed for the API when 'workflows' are supported
# TODO: Eventually this route will become the / route,
# but right now it is a placeholder while we build up the Workflows routes
# It's not included in the OpenAPI schema for now so it's not visible in the docs
@router.post("/new", status_code=status.HTTP_201_CREATED, include_in_schema=True)
def create_experiment_id(service: ExperimentServiceDep, request: ExperimentIdCreate) -> GetExperimentResponse:
    """Create an experiment ID."""
    # FIXME Shouldn't the model set this
    return GetExperimentResponse.model_validate(service.create_experiment(request).model_dump())


# TODO: FIXME this should not need the /all suffix.
# See further discussion https://github.com/mozilla-ai/lumigator/pull/728/files/2c960962c365d72e0714a16333884f0f209d214e#r1932176937
@router.get("/new/all", include_in_schema=False)
def list_experiments_new(
    service: ExperimentServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[GetExperimentResponse]:
    """List all experiments."""
    return ListingResponse[GetExperimentResponse].model_validate(service.list_experiments(skip, limit).model_dump())


@router.get("/new/{experiment_id}", include_in_schema=False)
def get_experiment_new(service: ExperimentServiceDep, experiment_id: str) -> GetExperimentResponse:
    """Get an experiment by ID."""
    return GetExperimentResponse.model_validate(service.get_experiment(experiment_id).model_dump())


@router.delete("/new/{experiment_id}", include_in_schema=False)
def delete_experiment_new(service: ExperimentServiceDep, experiment_id: str) -> None:
    """Delete an experiment by ID."""
    service.delete_experiment(experiment_id)
