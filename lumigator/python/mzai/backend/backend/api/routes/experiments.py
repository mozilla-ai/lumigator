from uuid import UUID

from fastapi import APIRouter, status
from lumigator_schemas.experiments import (
    ExperimentCreate,
    ExperimentResponse,
    ExperimentResultDownloadResponse,
    ExperimentResultResponse,
)
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    JobEvalCreate,
)

from backend.api.deps import JobServiceDep

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_experiment(
    service: JobServiceDep,
    request: ExperimentCreate,
) -> ExperimentResponse:
    return service.create_job(JobEvalCreate.model_validate(request.model_dump()))


@router.get("/{experiment_id}")
def get_experiment(service: JobServiceDep, experiment_id: UUID) -> ExperimentResponse:
    return ExperimentResponse.model_validate(
        service.get_job(experiment_id).model_dump()
        )


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
