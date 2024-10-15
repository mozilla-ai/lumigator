from http import HTTPStatus

from schemas.deployments import DeploymentEvent

from schemas.jobs import JobSubmissionResponse
from sdk.client import ApiClient


class HealthCheck:
    def __init__(self):
        self.status = ""
        self.deployment_type = ""

    def ok(self):
        return self.status == "OK"


class Health:
    HEALTH_ROUTE = "health"

    def __init__(self, c: ApiClient):
        self.__client = c

    def healthcheck(self) -> HealthCheck | None:
        """Returns healthcheck information."""
        check = HealthCheck()
        response = self.__client.get_response(self.HEALTH_ROUTE)
        if not response:
            return None

        data = response.json()
        check.status = data.get("status")
        check.deployment_type = data.get("deployment_type")

        return check

    def get_deployments(self) -> list[DeploymentEvent]:
        response = self.__client.get_response(f"{self.HEALTH_ROUTE}/deployments")

        if not response:
            return []

        return [DeploymentEvent(**args) for args in response.json()]

    def get_jobs(self) -> list[JobSubmissionResponse]:
        """Returns information on all job submissions."""
        endpoint = f"{self.HEALTH_ROUTE}/jobs/"
        response = self.__client.get_response(endpoint)

        if not response:
            return []

        return [JobSubmissionResponse(**job) for job in response.json()]

    def get_job(self, job_id: str) -> JobSubmissionResponse | None:
        """Returns information on the job submission for the specified ID."""
        endpoint = f"{self.HEALTH_ROUTE}/jobs/{job_id}"
        response = self.__client.get_response(endpoint)

        if not response or response.status_code != HTTPStatus.OK:
            return None

        data = response.json()
        return JobSubmissionResponse(**data)
