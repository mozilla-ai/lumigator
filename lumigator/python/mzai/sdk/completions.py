import json
from http import HTTPMethod, HTTPStatus

from schemas.completions import CompletionResponse

from client import ApiClient


class Completions:
    COMPLETIONS_ROUTE = "completions"

    def __init__(self, c: ApiClient):
        self.client = c

    def get_vendors(self) -> list[str]:
        """Returns the list of supported external vendors."""
        response = self.client.get_response(self.COMPLETIONS_ROUTE)

        if not response:
            return []

        return [str(vendor) for vendor in response.json()]

    def get_completion(self, vendor: str, text: str) -> CompletionResponse | None:
        """Returns completions from the specified vendor for given text (prompt)."""

        # Sanitize the inputs.
        vendor = vendor.lower()
        text = text.strip()

        # Validate that the requested vendor is supported.
        if vendor not in [v.lower() for v in self.get_vendors()]:
            raise ValueError(f"vendor '{vendor}' not supported")

        # Validate we have some text input as our prompt.
        if text == "":
            raise ValueError("text cannot be empty or whitespace")

        endpoint = f"{self.COMPLETIONS_ROUTE}/{vendor}/"
        response = self.client.get_response(
            endpoint, HTTPMethod.POST, json.load(f'{{"text":"{text}"}}')
        )

        if not response or response.status_code != HTTPStatus.OK:
            return None

        data = response.json()
        return CompletionResponse(**data)
