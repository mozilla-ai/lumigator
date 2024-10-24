from lumigator_sdk.client import ApiClient
from lumigator_sdk.completions import Completions
from lumigator_sdk.experiments import Experiments
from lumigator_sdk.health import Health
from lumigator_sdk.lm_datasets import Datasets


class LumigatorClient:
    def __init__(self, api_host: str):
        self.client = ApiClient(api_host)

        self.completions = Completions(self.client)
        self.experiments = Experiments(self.client)
        self.health = Health(self.client)
        self.datasets = Datasets(self.client)
