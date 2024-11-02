"""Jobs SDK

Provides a class to manipulate jobs in Lumigator.
"""

import asyncio
from http import HTTPMethod
from uuid import UUID

from schemas.extras import ListingResponse
from schemas.jobs import (
    JobEvalCreate,
    JobResponse,
    JobResultDownloadResponse,
    JobResultResponse,
    JobType,
)

from sdk.client import ApiClient


class Jobs:
    JOBS_ROUTE = "jobs"

    def __init__(self, c: ApiClient):
        self.client = c

    def get_jobs(self) -> ListingResponse[JobResponse]:
        """Returns information on all jobs.

        Returns:
            ListingResponse[JobResponse]: all existing jobs.
        """
        response = self.client.get_response(self.JOBS_ROUTE)

        if not response:
            return []

        return ListingResponse[JobResponse](**response.json())

    def get_job(self, id: UUID) -> JobResponse:
        """Returns information on a specific job.

        Args:
            id (UUID): the id of the job to retrieve
        Returns:
            JobResponse: the job information for the provided id.
        """
        response = self.client.get_response(f"{self.JOBS_ROUTE}/{id}")

        if not response:
            return []

        return JobResponse(**(response.json()))

    async def wait_for_job(self, id: UUID, retries: int = 30, poll_wait: int = 30) -> JobResponse:
        """Waits for a job to succeed and returns its latest retrieved information.

        Args:
            id (UUID): the id of the job to wait for
            retries (int):
            poll_wait (int):
        Returns:
            JobResponse: the most recently job information for the id, when the job has finished
        """
        for _ in range(1, retries):
            # http://localhost:8265/api/jobs/f311fa44-025a-4703-b8ba-7e0b1001b484
            response = self.client.get_ray_job_response(f"{id}")
            # response = requests.get(f"http://localhost:8265/api/jobs/{id}")
            jobinfo = response.json()
            if jobinfo["status"] == "PENDING" or jobinfo["status"] == "RUNNING":
                await asyncio.sleep(poll_wait)
                continue
            elif jobinfo["status"] == "FAILED":
                raise Exception(f"Job {id} failed")
            elif jobinfo["status"] == "STOPPED":
                raise Exception(f"Job {id} stopped")
            elif jobinfo["status"] == "SUCCEEDED":
                return jobinfo
        raise Exception(
            f"Job {id} did not complete in the polling "
            "time (retries: {retries}, poll_wait: {poll_wait})"
        )

    def create_job(self, type: JobType, request: JobEvalCreate) -> JobResponse:
        """Creates a new job.

        Args:
            type(JobType): the kind of job to create.
            request(JobEvalCreate): the specific details about the job that needs to be created.

        Returns:
            JobResponse: the information for the newly created job.
        """
        response = self.client.get_response(
            f"{self.JOBS_ROUTE}/{type.value}/",
            method=HTTPMethod.POST,
            data=request.model_dump_json(),
        )

        if not response:
            return []

        return JobResponse(**(response.json()))

    def get_job_result(self, id: UUID) -> JobResultResponse:
        """Returns the results of a specific job.

        Args:
            id (str): the id of the job results to retrieve
        Returns:
            JobResultResponse: the job results for the provided id.
        """
        response = self.client.get_response(f"{self.JOBS_ROUTE}/{id}")

        if not response:
            return []

        return JobResultResponse(**(response.json()))

    def get_job_download(self, id: UUID) -> JobResultDownloadResponse:
        """Returns the download link for the results of a specific job.

        Args:
            id (str): the id of the job download link to retrieve
        Returns:
            JobResultDownloadResponse: the job download link for the provided id.
        """
        response = self.client.get_response(f"{self.JOBS_ROUTE}/{id}/result/download")

        if not response:
            return []

        return JobResultDownloadResponse(**(response.json()))
