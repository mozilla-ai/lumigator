from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.models import ModelsResponse

from lumigator_sdk.client import ApiClient


class Models:
    MODELS_ROUTE = "models"

    def __init__(self, c: ApiClient):
        """Construct a new instance of the Models class.

        Args:
            c (ApiClient): The API client to use for requests.

        Returns:
            Models: A new Models instance.
        """
        self.client = c

    def get_suggested_models(self, task_name: str) -> ListingResponse[ModelsResponse]:
        """Return information on all suggested models.

        .. admonition:: Example

            .. code-block:: python

                from lumigator_sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("localhost:8000")
                lm_client.models.get_suggested_models("summarization")

        Args:
            task_name (str): The name of the task to get the suggested models for.

        Returns:
            ListingResponse[dic]: All suggested models.
        """
        response = self.client.get_response(f"{self.MODELS_ROUTE}/{task_name}")

        return ListingResponse[ModelsResponse](**response.json())
