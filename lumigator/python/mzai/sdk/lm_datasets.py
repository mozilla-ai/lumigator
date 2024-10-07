
from schemas.datasets import DatasetResponse

from client import ApiClient

class Datasets:
    DATASETS_ROUTE = "datasets"

    def __init__(self, c: ApiClient):
        self.client = c

    def get_datasets(self) -> list[DatasetResponse]:
        response = self.client.get_response(self.DATASETS_ROUTE)

        if not response:
            return []

        return [DatasetResponse(**args) for args in response.json()]