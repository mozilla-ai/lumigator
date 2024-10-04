from pathlib import Path

from sdk.core import COMPLETIONS_ROUTE


def get_vendors(self) -> list[str]:
    """Returns the list of supported external vendors."""
    endpoint = Path(self._api_url) / COMPLETIONS_ROUTE
    response = self.__get_response(endpoint)

    if not response:
        return []

    return [str(vendor) for vendor in response.json()]

