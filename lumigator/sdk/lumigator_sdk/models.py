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

    def get_suggested_models(self, tasks: list[str] = None) -> ListingResponse[ModelsResponse]:
        """Return information on suggested models filtered by tasks.

        .. admonition:: Example

            .. code-block:: python

                from lumigator_sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("localhost:8000")
                # Get models for a single task
                lm_client.models.get_suggested_models(["summarization"])
                # Get models for multiple tasks
                lm_client.models.get_suggested_models(["summarization", "translation"])
                # Get all models
                lm_client.models.get_suggested_models()

        Args:
            tasks (list[str], optional): The tasks to get suggested models for.
                If None, returns all models.

        Returns:
            ListingResponse[ModelsResponse]: Suggested models matching the specified tasks.
        """
        # Default route when no tasks are specified
        route = self.MODELS_ROUTE

        # Update route if tasks are specified
        if tasks:
            task_params = "&".join([f"tasks={task}" for task in tasks])
            route = f"{route}/?{task_params}"

        response = self.client.get_response(route)

        return ListingResponse[ModelsResponse](**response.json())
