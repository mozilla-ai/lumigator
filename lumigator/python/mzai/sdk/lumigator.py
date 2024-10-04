from sdk.client import ApiClient
from sdk.completions import Completions
from sdk.datasets import Datasets
from sdk.experiements import Experiments
from sdk.health import Health


class LumigatorClient:
    def __init__(self, api_host: str):
        self.client = ApiClient(api_host)

        self.completions = Completions(self.client)
        self.datasets = Datasets(self.client)
        self.experiments = Experiments(self.client)
        self.health = Health(self.client)