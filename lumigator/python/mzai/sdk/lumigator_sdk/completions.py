from http import HTTPMethod, HTTPStatus

from lumigator_schemas.completions import CompletionResponse

from lumigator_sdk.client import ApiClient


class Completions:
    COMPLETIONS_ROUTE = "completions"

    def __init__(self, c: ApiClient):
        """Construct a new instance of the Completions class.

        Args:
            c (ApiClient): The API client to use for requests.

        Returns:
            Completions: A new Completions instance.
        """
        self.__client = c
        self.__cached_vendors = self.get_vendors()

    def get_vendors(self) -> list[str]:
        """Return the list of supported external vendors.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.completions.get_vendors()

        Returns:
            list[str]: A list of supported vendors.
        """
        response = self.__client.get_response(self.COMPLETIONS_ROUTE)

        if not response:
            return []

        # Update the cached vendors.
        self.__cached_vendors = [str(vendor).lower() for vendor in response.json()]

        return self.__cached_vendors

    def get_completion(self, vendor: str, text: str) -> CompletionResponse | None:
        """Return completions from the specified vendor for given prompt.

        .. admonition:: Example

            .. code-block:: python

                from sdk.lumigator import LumigatorClient

                lm_client = LumigatorClient("http://localhost:8000")
                lm_client.completions.get_completion("openai", "Once upon a time")

        Args:
            vendor (str): The vendor to use for completion.
            text (str): The prompt text to generate completions for.

        Returns:
            CompletionResponse | `None`: The completion response or `None` if
                the request failed.
        """
        # Sanitize the inputs.
        vendor = vendor.lower()
        text = text.strip()

        # Attempt to validate vendors using the cache.
        if vendor not in self.__cached_vendors:
            raise ValueError(
                f"vendor: '{vendor}' was not found in cache, 'get_vendors' to update cache)"
            )

        # Validate we have some text input as our prompt.
        if text == "":
            raise ValueError("text: cannot be empty or whitespace")

        endpoint = f"{self.COMPLETIONS_ROUTE}/{vendor}/"
        response = self.__client.get_response(
            endpoint, HTTPMethod.POST, json_data={"text": text}
        )

        if not response or response.status_code != HTTPStatus.OK:
            return None

        data = response.json()
        return CompletionResponse(**data)
