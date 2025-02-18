"""Jobs SDK

Provides a class to manipulate jobs in Lumigator.
"""

import time
from http import HTTPMethod
from uuid import UUID

from lumigator_schemas.datasets import DatasetResponse
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    Job,
    JobAnnotateConfig,
    JobCreate,
    JobEvalConfig,
    JobInferenceConfig,
    JobResponse,
    JobResultDownloadResponse,
    JobResultResponse,
    JobType,
)

from lumigator_sdk.client import ApiClient
from lumigator_sdk.strict_schemas import (
    JobAnnotateConfig as JobAnnotateConfigStrict,
)
from lumigator_sdk.strict_schemas import (
    JobCreate as JobCreateStrict,
)
from lumigator_sdk.strict_schemas import (
    JobEvalConfig as JobEvalConfigStrict,
)
from lumigator_sdk.strict_schemas import (
    JobInferenceConfig as JobInferenceConfigStrict,
)


class Jobs:
    JOBS_ROUTE = "jobs"

    def __init__(self, c: ApiClient):
        """Construct a new instance of the Jobs class.

        Args:
            c (ApiClient): the API client to use for requests.

        Returns:
            Jobs: a new Jobs instance.
        """
        self.client = c

    def get_jobs(self, skip=0, limit=None) -> ListingResponse[Job]:
        """Return information on all jobs.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.jobs.get_jobs()

        Returns:
            ListingResponse[JobResponse]: All existing jobs.
        """
        response = self.client.get_response(self.JOBS_ROUTE)

        return ListingResponse[Job](**response.json())

    def get_jobs_per_type(self, job_type: JobType, skip=0, limit=None) -> ListingResponse[Job]:
        """Return information on jobs of a specific type.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.jobs.get_jobs_per_type(JobType.EVALUATION)

        Returns:
            ListingResponse[JobResponse]: All existing jobs.
        """
        response = self.client.get_response(f"{self.JOBS_ROUTE}?job_types={job_type.value}")

        return ListingResponse[Job](**response.json())

    def get_job(self, id: UUID) -> Job:
        """Return information on a specific job.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.jobs.get_job(job_id)

        Args:
            id (UUID): the ID of the job to retrieve
        Returns:
            JobResponse: The job information for the provided ID.
        """
        response = self.client.get_response(f"{self.JOBS_ROUTE}/{id}")

        return Job(**(response.json()))

    def get_job_dataset(self, id: UUID) -> DatasetResponse:
        """Return the dataset created by a specific job.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.jobs.get_job_dataset(job_id)

        Args:
            id (UUID): the ID of the job to retrieve
        Returns:
            JobResponse: The job information for the provided ID.
        """
        response = self.client.get_response(f"{self.JOBS_ROUTE}/{id}/dataset")

        return DatasetResponse(**(response.json()))

    def wait_for_job(self, id: UUID, retries: int = 180, poll_wait: int = 5) -> JobResponse:
        """Wait for a job to succeed and return latest retrieved information.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                job = lm_client.jobs.wait_for_job(job_id)

        Args:
            id (UUID): The ID of the job to wait for.
            retries (int): The number of times to poll for the job status.
            poll_wait (int): The time to wait between polling attempts.

        Returns:
            JobResponse: the most recently job information for the ID, when the
              job has finished
        """
        for _ in range(1, retries):
            response = self.client.get_ray_job_response(f"{id}")
            jobinfo = response.json()
            if jobinfo["status"] == "PENDING" or jobinfo["status"] == "RUNNING":
                time.sleep(poll_wait)
                continue
            elif jobinfo["status"] == "FAILED":
                raise Exception(f"Job {id} failed")
            elif jobinfo["status"] == "STOPPED":
                raise Exception(f"Job {id} stopped")
            elif jobinfo["status"] == "SUCCEEDED":
                return jobinfo
        raise Exception(f"Job {id} did not complete in the polling time (retries: {retries}, poll_wait: {poll_wait})")

    def create_job(self, request: JobCreate) -> JobResponse:
        """Create a new job.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient
                from lumigator_schemas.jobs import JobCreate, JobEvalConfig

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.jobs.create_job(JobCreate(JobEvalConfig))

        Args:
            request(JobCreate): The job's configuration. Its job_type
                can be ANNOTATION, EVALUATION, or INFERENCE.

        Returns:
            JobResponse: The information for the newly created job.
        """
        JobCreateStrict.model_validate(JobCreate.model_dump(request))
        if request.job_config.job_type == JobType.ANNOTATION:
            JobAnnotateConfigStrict.model_validate(JobAnnotateConfig.model_dump(request.job_config))
        elif request.job_config.job_type == JobType.EVALUATION:
            JobEvalConfigStrict.model_validate(JobEvalConfig.model_dump(request.job_config))
        elif request.job_config.job_type == JobType.INFERENCE:
            JobInferenceConfigStrict.model_validate(JobInferenceConfig.model_dump(request.job_config))

        response = self.client.get_response(
            f"{self.JOBS_ROUTE}/{request.job_config.job_type.value}/",
            method=HTTPMethod.POST,
            data=request.model_dump_json(),
        )

        return JobResponse(**(response.json()))

    def get_job_result(self, id: UUID) -> JobResultResponse:
        """Return the results of a specific job.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.jobs.get_job_result(job_id)

        Args:
            id (str): The ID of the job results to retrieve.

        Returns:
            JobResultResponse: The job results for the provided ID.
        """
        response = self.client.get_response(f"{self.JOBS_ROUTE}/{id}")

        return JobResultResponse(**(response.json()))

    def get_job_download(self, id: UUID) -> JobResultDownloadResponse:
        """Return the download link for the results of a specific job.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.jobs.get_job_download(job_id)

        Args:
            id (str): The ID of the job download link to retrieve.

        Returns:
            JobResultDownloadResponse: The job download link for the provided
                ID.
        """
        response = self.client.get_response(f"{self.JOBS_ROUTE}/{id}/result/download")

        return JobResultDownloadResponse(**(response.json()))
