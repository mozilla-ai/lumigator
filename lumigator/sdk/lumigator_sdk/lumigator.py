from urllib3 import Retry

from lumigator_sdk.client import ApiClient
from lumigator_sdk.experiments import Experiments
from lumigator_sdk.health import Health
from lumigator_sdk.jobs import Jobs
from lumigator_sdk.lm_datasets import Datasets
from lumigator_sdk.models import Models
from lumigator_sdk.workflows import Workflows

# Only retries initial connections
# No HTTP errors are retried
DEFAULT_RETRY = Retry(
    connect=5,
    backoff_factor=1,
    backoff_max=20,
)


class LumigatorClient:
    def __init__(
        self,
        api_host: str,
        ray_host: str = "127.0.0.1:8265",
        retry_conf: Retry | None = DEFAULT_RETRY,
    ):
        """Construct a new LumigatorClient instance.

        Construct a new LumigatorClient instance with a given API and Ray host.
        The client provides access to the Lumigator API, permitting users to
        interact with the Lumigator services.

        .. admonition:: Example

                .. code-block:: python

                    from sdk.lumigator import LumigatorClient

                    lm_client = LumigatorClient("http://localhost:8000")

        Args:
            api_host (str): The API host to connect to.
            ray_host (str): The Ray host to connect to. Defaults to
                `127.0.0.1:8265`.

        Returns:
            LumigatorClient: A new LumigatorClient instance.
        """
        self.client = ApiClient(api_host, ray_host, retry_conf)

        self.health = Health(self.client)
        if self.health.healthcheck() is None:
            raise Exception("LumigatorClient cannot connect")
        self.jobs = Jobs(self.client)
        self.datasets = Datasets(self.client)
        self.models = Models(self.client)
        self.workflows = Workflows(self.client)
        self.experiments = Experiments(self.client)
