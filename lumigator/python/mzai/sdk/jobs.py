from http import HTTPStatus
from pathlib import Path

from mzai.backend.schemas.jobs import JobSubmissionResponse
from sdk.core import HEALTH_ROUTE


def get_jobs(self) -> list[JobSubmissionResponse]:
    """Returns information on all job submissions."""
    endpoint = Path(self._api_url) / f"{HEALTH_ROUTE}/jobs/"
    response = self.__get_response(endpoint)

    if not response:
        return []

    return [JobSubmissionResponse(**job) for job in response.json()]


def get_job(self, job_id: str) -> JobSubmissionResponse | None:
    """Returns information on the job submission for the specified ID."""
    endpoint = Path(self._api_url) / f"{HEALTH_ROUTE}/jobs/{job_id}"
    response = self.__get_response(endpoint)

    if not response or response.status_code != HTTPStatus.OK:
        return None

    data = response.json()
    return JobSubmissionResponse(**data)