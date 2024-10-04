from pathlib import Path

from schemas.datasets import DatasetResponse

from sdk.core import ApiClient


class Datasets:
    DATASETS_ROUTE = "datasets"

    def __init__(self, c: ApiClient):
        self.client = c

    def get_datasets(self) -> list[DatasetResponse]:
        response = self.client.__get_response(str(Path(self._api_url) / self.DATASETS_ROUTE))

        if not response:
            return []

        return [DatasetResponse(**args) for args in response.json()]