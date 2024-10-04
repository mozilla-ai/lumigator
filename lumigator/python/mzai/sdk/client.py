import json
from http import HTTPMethod, HTTPStatus
from typing import Any, Dict  # noqa: UP035

import requests
from loguru import logger
from requests.exceptions import HTTPError


def _make_request(
        url: str,
        method: str = "GET",
        params: Dict[str, Any] = None,  # noqa: UP006
        data: Dict[str, Any] = None,  # noqa: UP006
        files: Dict[str, Any] = None,  # noqa: UP006
        headers: Dict[str, str] = None,  # noqa: UP006
        json_: Dict[str, str] = None,  # noqa: UP006
        timeout: int = 10,
        verbose: bool = True,
        *args,
        **kwargs,
) -> requests.Response:
    """HTTP Request using requests
    Args:
        url (str)
        method (str, optional): The HTTP method to use. Defaults to "GET".
        params (Dict[str, Any], optional): URL parameters to include in the request.
        data (Dict[str, Any], optional): Data to send in the request body.
        files (Dict[str, Any], optional): Files to send in the request body.
        headers (Dict[str, str], optional): Headers to include in the request.
        timeout (int, optional): Timeout for the request in seconds. Defaults to 10.

    Returns:
        requests.Response: The response object from the request.

    Raises:
        requests.RequestException
    """
    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            params=params,
            data=data,
            files=files,
            headers=headers,
            timeout=timeout,
            json=json_,
            *args,  # noqa: B026
            **kwargs,  # noqa: B026
        )
        response.raise_for_status()
        if verbose:
            logger.info(f"{json.dumps(response.json(), indent=2)}")
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise
    return response


class ApiClient:
    def __init__(self, api_host: str):
        self.api_host = api_host
        # NOTE: do we only support HTTP?
        self._api_url = f"http://{self.api_host}/api/v1"

    def get_response(self, api_path, method: HTTPMethod=HTTPMethod.GET, data=None, verbose: bool = True) -> requests.Response:
        """Makes a request to the specified path and attempts to return the response.
        Raises an exception for any error other than 404 - NOT FOUND.
        """
        path = f"{self._api_url.rstrip('/')}/{api_path.lstrip('/')}"

        try:
            response = _make_request(path, data, method=method, verbose=verbose)
            # Support returning a response for 200-204 status codes.
            # NOTE: Other status codes that are returned without an HTTP error aren't supported.
            # e.g. 307 - Temporary Redirect
            if HTTPStatus.OK <= response.status_code <= HTTPStatus.NO_CONTENT:
                return response
        except HTTPError as e:
            if e.response.status_code == HTTPStatus.NOT_FOUND:
                return e.response
            else:
                # Re-raise the exception if it's not a 404 error
                # This happens for status codes such as 400 - Bad Request etc.
                raise
        except requests.RequestException as e:
            # TODO: Don't log and raise
            logger.error(f"An error occurred: {e}")
            raise

