from lumigator_sdk.client import ApiClient


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
