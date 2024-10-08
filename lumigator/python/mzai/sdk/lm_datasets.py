from schemas.datasets import DatasetFormat, DatasetResponse, DatasetDownloadResponse
from schemas.extras import ListingResponse

from uuid import UUID
from http import HTTPMethod

from json import dumps

from client import ApiClient


class Datasets:
    DATASETS_ROUTE = "datasets"

    def __init__(self, c: ApiClient):
        self.client = c

    def get_datasets(self) -> ListingResponse[DatasetResponse]:
        response = self.client.get_response(self.DATASETS_ROUTE)

        if not response:
            return []

        return [DatasetResponse(**args) for args in response.json()]

    def get_dataset(self, id: str) -> DatasetResponse:
        UUID(id)
        endpoint = f"{self.DATASETS_ROUTE}/{id}/download"
        response = self.client.get_response(endpoint)

        if not response:
            return []

        return DatasetResponse(**(response.json()))

    def post_dataset(self, id: str, dataset: bytearray, format: DatasetFormat) -> DatasetResponse:
        UUID(id)
        files = {"dataset": dataset, "format": (None, str(format))}
        response = self.client.get_response(
            self.DATASETS_ROUTE, HTTPMethod.POST, data=None, files=files
        )

        if not response:
            return []

        return DatasetResponse(**(response.json()))

    def delete_dataset(self, id: str) -> None:
        UUID(id)
        self.client.get_response(self.DATASETS_ROUTE)

    def get_dataset_link(self, id: str) -> DatasetDownloadResponse:
        UUID(id)
        response = self.client.get_response(self.DATASETS_ROUTE, HTTPMethod.DELETE)

        if not response:
            return []

        return DatasetDownloadResponse(**(response.json()))
