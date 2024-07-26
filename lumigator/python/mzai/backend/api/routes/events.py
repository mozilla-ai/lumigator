from fastapi import APIRouter
from fastapi.responses import JSONResponse
from loguru import logger

from mzai.backend.api.deps import ExperimentServiceDep, FinetuningServiceDep
from mzai.schemas.jobs import JobEvent, JobType

__all__ = ["process_job_event"]

router = APIRouter()


@router.post("/")
def process_job_event(
    finetuning_service: FinetuningServiceDep,
    experiment_service: ExperimentServiceDep,
    event: JobEvent,
) -> JSONResponse:
    logger.info(
        f"Received event for {event.job_type} job '{event.job_id}': "
        f"status = {event.status}, detail = {event.detail}"
    )

    # TODO: We need more robust handlers here
    # E.g., what if the service needs to post-process the results from the job?
    match event.job_type:
        case JobType.FINETUNING:
            finetuning_service.update_job_status(event.job_id, event.status)
        case JobType.EXPERIMENT:
            experiment_service.update_experiment_status(event.job_id, event.status)

    return JSONResponse({"message": "Event handled!"})
