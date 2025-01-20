from http import HTTPMethod
from io import IOBase
from uuid import UUID

from lumigator_schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse
from lumigator_schemas.extras import ListingResponse

from lumigator_sdk.client import ApiClient


class Datasets:
    DATASETS_ROUTE = "datasets"

    def __init__(self, c: ApiClient):
        """Construct a new instance of the Datasets class.

        Args:
            c (ApiClient): The API client to use for requests.

        Returns:
            Datasets: A new Datasets instance.
        """
        self.client = c

    def get_datasets(self) -> ListingResponse[DatasetResponse]:
        """Return information on all datasets.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.datasets.get_datasets()

        Returns:
            ListingResponse[DatasetResponse]: All existing datasets.
        """
        response = self.client.get_response(self.DATASETS_ROUTE)

        return ListingResponse[DatasetResponse](**response.json())

    def get_dataset(self, id: UUID) -> DatasetResponse:
        """Return information on a specific dataset.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.datasets.get_dataset(dataset_id)

        Args:
            id (UUID): The ID of the dataset to retrieve
        Returns:
            DatasetResponse: the dataset information for the provided ID.
        """
        response = self.client.get_response(f"{self.DATASETS_ROUTE}/{id}")

        return DatasetResponse(**(response.json()))

    def create_dataset(self, dataset: IOBase, format: DatasetFormat) -> DatasetResponse:
        """Create a new dataset.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.datasets.create_dataset(dataset, dataset_format)

        Args:
            dataset(IOBase): a bytes-like object containing the dataset itself.
            format(DatasetFormat): currently, always `DatasetFormat.JOB`.

        Returns:
            DatasetResponse: the information for the newly created dataset.
        """
        files = {"dataset": dataset, "format": (None, format.value)}
        response = self.client.get_response(
            self.DATASETS_ROUTE, method=HTTPMethod.POST, data=None, files=files
        )

        return DatasetResponse(**(response.json()))

    def delete_dataset(self, id: UUID) -> None:
        """Delete a specific dataset.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.datasets.delete_dataset(dataset_id)

        Args:
            id (UUID): the ID of the dataset to retrieve
        """
        self.client.get_response(f"{self.DATASETS_ROUTE}/{id}", method=HTTPMethod.DELETE)

    def get_dataset_link(self, id: UUID, extension: str | None = None) -> DatasetDownloadResponse:
        """Return the download link for a specific dataset.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.datasets.get_dataset_link(dataset_id)

        Args:
            id (UUID): the ID of the dataset whose download link we want to
                obtain.

            extension (str): when specified, will be used to return only URLs for files which have
                a matching file extension. Wildcards are not accepted. By default, all files are
                returned. e.g. csv.

        Returns:
            DatasetDownloadResponse: the download link for the requested
                dataset.
        """
        extension = extension.strip().lower() if extension and extension.strip() else None

        endpoint = (
            f"{self.DATASETS_ROUTE}/{id}/download"
            f"{f'?extension={extension}' if extension is not None else ''}"
        )
        response = self.client.get_response(endpoint)

        return DatasetDownloadResponse(**(response.json()))
