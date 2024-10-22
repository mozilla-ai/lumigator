"""
Jobs SDK

Provides a class to manipulate jobs in Lumigator.
"""

from schemas.jobs import JobCreate, JobResponse, JobResultResponse, JobResultDownloadResponse, JobType
from schemas.extras import ListingResponse

from uuid import UUID
from http import HTTPMethod

from io import IOBase
from sdk.client import ApiClient
from loguru import logger

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
            id (str): the id of the job to retrieve
        Returns:
            JobResponse: the job information for the provided id.
        """
        response = self.client.get_response(f"{self.JOBS_ROUTE}/{id}")

        if not response:
            return []

        return JobResponse(**(response.json()))


    def create_job(self, type: JobType, request: JobCreate) -> JobResponse:
        """
        Creates a new job.
        Args:
            type(JobType): the kind of job to create.
            request(JobCreate): the specific details about the job that needs to be created.
        Returns:
            JobResponse: the information for the newly created dataset.
        """
        response = self.client.get_response(
            f"{self.JOBS_ROUTE}/{type.value}", method=HTTPMethod.POST, data=request
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
        response = self.client.get_response(f"{self.JOBS_ROUTE}/{id}")

        if not response:
            return []

        return JobResultDownloadResponse(**(response.json()))











