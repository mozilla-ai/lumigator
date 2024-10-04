import json
from http import HTTPMethod, HTTPStatus

from schemas.completions import CompletionResponse

from sdk.client import ApiClient


class Completions:
    COMPLETIONS_ROUTE = "completions"

    def __init__(self, c:ApiClient):
        self.client = c

    def get_vendors(self) -> list[str]:
        """Returns the list of supported external vendors."""
        response = self.client.get_response(self.COMPLETIONS_ROUTE)

        if not response:
            return []

        return [str(vendor) for vendor in response.json()]


    def get_completion(self, vendor: str, text: str) -> CompletionResponse | None:
        vendor = vendor.lower
        if vendor not in ["mistral", "openai"]:
            # TODO: invalid vendor
            raise

        endpoint = f"{self.COMPLETIONS_ROUTE}/{vendor}/"
        response = self.client.get_response(endpoint, HTTPMethod.POST, json.load('{"text":"foo"}'))

        if not response or response.status_code != HTTPStatus.OK:
            return None

        data = response.json()
        return CompletionResponse(**data)
