from client import ApiClient
from completions import Completions
from experiments import Experiments
from health import Health


class LumigatorClient:
    def __init__(self, api_host: str):
        self.client = ApiClient(api_host)

        self.completions = Completions(self.client)
        self.experiments = Experiments(self.client)
        self.health = Health(self.client)
