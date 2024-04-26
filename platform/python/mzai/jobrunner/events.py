from uuid import UUID

import requests
from loguru import logger

from mzai.jobrunner.settings import settings
from mzai.schemas.jobs import JobEvent, JobStatus, JobType


def send_job_event(
    job_id: UUID,
    job_type: JobType,
    status: JobStatus,
    detail: str | None = None,
) -> None:
    event = JobEvent(job_id=job_id, job_type=job_type, status=status, detail=detail)
    logger.info(f"Sending job event {event}")
    response = requests.post(
        url=settings.BACKEND_EVENTS_URL,
        json=event.model_dump(mode="json"),
    )
    if response.status_code != 200:
        logger.error(f"Failed to send event for job '{job_id}': {response.json()}")
