"""
Dataset SDK

Provides a class to manipulate datasets in Lumigator.
"""

from schemas.datasets import DatasetFormat, DatasetResponse, DatasetDownloadResponse
from schemas.extras import ListingResponse

from uuid import UUID
from http import HTTPMethod

from io import IOBase
from client import ApiClient
from loguru import logger


class Datasets:
    DATASETS_ROUTE = "datasets"

    def __init__(self, c: ApiClient):
        self.client = c

    def get_datasets(self) -> ListingResponse[DatasetResponse]:
        """Returns information on all datasets.
        Returns:
            ListingResponse[DatasetResponse]: all existing datasets.
        """
        response = self.client.get_response(self.DATASETS_ROUTE)

        if not response:
            return []

        return ListingResponse[DatasetResponse](**response.json())

    def get_dataset(self, id: UUID) -> DatasetResponse:
        """Returns information on a specific dataset.
        Args:
            id (str): the id of the dataset to retrieve
        Returns:
            DatasetResponse: the dataset information for the provided id.
        """
        response = self.client.get_response(f"{self.DATASETS_ROUTE}/{id}")

        if not response:
            return []

        return DatasetResponse(**(response.json()))

    def create_dataset(self, dataset: IOBase, format: DatasetFormat) -> DatasetResponse:
        """
        Creates a new dataset.
        Args:
            dataset(IOBase): a bytes-like object containing the dataset itself.
            format(DatasetFormat): currently, always `DatasetFormat.EXPERIMENT`.
        Returns:
            DatasetResponse: the information for the newly created dataset.
        """
        files = {"dataset": dataset, "format": (None, format.value)}
        response = self.client.get_response(
            self.DATASETS_ROUTE, method=HTTPMethod.POST, data=None, files=files
        )

        if not response:
            return []

        return DatasetResponse(**(response.json()))

    def delete_dataset(self, id: UUID) -> None:
        """Deletes a specific dataset.
        Args:
            id (str): the id of the dataset to retrieve
        """
        self.client.get_response(f"{self.DATASETS_ROUTE}/{id}", method=HTTPMethod.DELETE)

    def get_dataset_link(self, id: UUID) -> DatasetDownloadResponse:
        """Returns the download link for a specific dataset.
        Args:
            id (str): the id of the dataset whose download link we want to obtain.
        Returns:
            DatasetDownloadResponse: the download link for the requested dataset.
        """
        endpoint = f"{self.DATASETS_ROUTE}/{id}/download"
        response = self.client.get_response(endpoint)

        if not response:
            return []

        return DatasetDownloadResponse(**(response.json()))
