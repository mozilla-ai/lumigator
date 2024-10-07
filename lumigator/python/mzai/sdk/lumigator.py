from sdk.client import ApiClient
from sdk.health import Health


class LumigatorClient:
    def __init__(self, api_host: str):
        self.client = ApiClient(api_host)

        self.health = Health(self.client)