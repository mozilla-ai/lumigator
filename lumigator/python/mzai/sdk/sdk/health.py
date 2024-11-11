from http import HTTPStatus

from schemas.jobs import JobSubmissionResponse

from sdk.client import ApiClient


class HealthCheck:
    def __init__(self):
        """Construct a new instance of the HealthCheck class.

        Attributes:
            status (str): The status of the healthcheck.
            deployment_type (str): The deployment type of the healthcheck.

        Returns:
            HealthCheck: A new HealthCheck instance.
        """
        self.status = ""
        self.deployment_type = ""

    def ok(self):
        """Always return status OK.

        Returns:
            str: Status OK.
        """
        return self.status == "OK"


class Health:
    HEALTH_ROUTE = "health"

    def __init__(self, c: ApiClient):
        """Construct a new instance of the Health class.

        Args:
            c (ApiClient): The API client to use for requests.

        Returns:
            Health: A new Health instance.
        """
        self.__client = c

    def healthcheck(self) -> HealthCheck | None:
        """Return healthcheck information.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.health.healthcheck()

        Returns:
            HealthCheck | ``None``: The healthcheck information.
        """
        check = HealthCheck()
        response = self.__client.get_response(self.HEALTH_ROUTE)
        if not response:
            return None

        data = response.json()
        check.status = data.get("status")
        check.deployment_type = data.get("deployment_type")

        return check

    def get_jobs(self) -> list[JobSubmissionResponse]:
        """Return information on all job submissions.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                jobs = lm_client.health.get_jobs()

        Returns:
            list[JobSubmissionResponse]: A list of job submission information.
        """
        endpoint = f"{self.HEALTH_ROUTE}/jobs"
        response = self.__client.get_response(endpoint)

        if not response:
            return []

        return [JobSubmissionResponse(**job) for job in response.json()]

    def get_job(self, job_id: str) -> JobSubmissionResponse | None:
        """Return information on the job submission for the specified ID.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                job_info = lm_client.health.get_job(job_id)

        Args:
            job_id (str): The ID of the job submission.

        Returns:
            JobSubmissionResponse | ``None``: The job submission information.
        """
        endpoint = f"{self.HEALTH_ROUTE}/jobs/{job_id}"
        response = self.__client.get_response(endpoint)

        if not response or response.status_code != HTTPStatus.OK:
            return None

        data = response.json()
        return JobSubmissionResponse(**data)
