import json
from http import HTTPMethod, HTTPStatus
from typing import Any, Dict  # noqa: UP035

import requests
from loguru import logger
from urllib3 import Retry


class ApiClient:
    def __init__(self, api_host: str, ray_host: str, retry_conf: Retry):
        """Base class for the Lumigator API client.

        Args:
            api_host (str): The host of the Lumigator backend API.
            ray_host (str): The host of the Ray cluster.
            retry_conf: an optional urllib3 retry strategy
        """
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_conf)

        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.api_host = api_host
        self.ray_host = ray_host
        # NOTE: Consider support for HTTPS too.
        self._api_url = f"http://{self.api_host}/api/v1"
        self._ray_url = f"http://{self.ray_host}/api/jobs"

    def _make_request(
        self,
        url: str,
        method: HTTPMethod = HTTPMethod.GET,
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
            response = self.session.request(
                method=str(method),
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
            if verbose and response.content:
                logger.info(f"{json.dumps(response.json(), indent=2)}")
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
        return response

    def get_response(
        self,
        api_path,
        method=HTTPMethod.GET,
        data=None,
        files=None,
        json_data=None,
        verbose: bool = False,
    ) -> requests.Response:
        """Make a request to the specified endpoint.

        Args:
            api_path (str): The path to make the request to.
            method (HTTPMethod, optional): The HTTP method to use.
                Defaults to ``HTTPMethod.GET``.
            data (optional): Dictionary, list of tuples, bytes, or file-like
                object to send in the body of the Request.
            files (optional): Dictionary of ``{'name': file-like-objects}`` (or
                ``{'name': file-tuple}``) for multipart encoding upload.
                ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``,
                3-tuple ``('filename', fileobj, 'content_type')`` or a 4-tuple
                ``('filename', fileobj, 'content_type', custom_headers)``,
                where ``content_type`` is a string defining the content type of
                the given file and ``custom_headers`` a dict-like object
                containing additional headers to add for the file.
            json_data (optional): A JSON serializable Python object to send in
                the body of the Request.
            verbose (bool, optional): Whether to log the response.
                Defaults to True.

        Returns:
            ``requests.Response``: The response object from the request.

        Raises:
            ``HTTPError``: Raises an exception for any error other than
                ``404 - NOT FOUND``.
            ``requests.RequestException``: Raises an exception for any other
                request error.
        """
        path = f"{self._api_url.rstrip('/')}/{api_path.lstrip('/')}"

        response = self._make_request(
            path, method, data=data, files=files, json_=json_data, verbose=verbose
        )
        # Support returning a response for 200-204 status codes.
        # NOTE: Other status codes that are returned without an HTTP error aren't supported.
        # e.g. 307 - Temporary Redirect
        if HTTPStatus.OK <= response.status_code <= HTTPStatus.NO_CONTENT:
            return response

    def get_ray_job_response(
        self,
        api_path,
        method=HTTPMethod.GET,
        data=None,
        files=None,
        json_data=None,
        verbose=True,
    ) -> requests.Response:
        """Make a request to the specified endpoint.

        Args:
            api_path (str): The path to make the request to.
            method (HTTPMethod, optional): The HTTP method to use.
                Defaults to ``HTTPMethod.GET``.
            data (optional): Dictionary, list of tuples, bytes, or file-like
                object to send in the body of the Request.
            files (optional): Dictionary of ``{'name': file-like-objects}`` (or
                ``{'name': file-tuple}``) for multipart encoding upload.
                ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``,
                3-tuple ``('filename', fileobj, 'content_type')`` or a 4-tuple
                ``('filename', fileobj, 'content_type', custom_headers)``,
                where ``content_type`` is a string defining the content type of
                the given file and ``custom_headers`` a dict-like object
                containing additional headers to add for the file.
            json_data (optional): A JSON serializable Python object to send in
                the body of the Request.
            verbose (bool, optional): Whether to log the response.
                Defaults to True.

        Returns:
            ``requests.Response``: The response object from the request.

        Raises:
            ``HTTPError``: Raises an exception for any error other than
                ``404 - NOT FOUND``.
            ``requests.RequestException``: Raises an exception for any other
                request-related error.
        """
        path = f"{self._ray_url.rstrip('/')}/{api_path.lstrip('/')}"

        response = self._make_request(
            path, method, data=data, files=files, json_=json_data, verbose=verbose
        )
        # Support returning a response for 200-204 status codes.
        # NOTE: Other status codes that are returned without an HTTP error aren't supported.
        # e.g. 307 - Temporary Redirect
        if HTTPStatus.OK <= response.status_code <= HTTPStatus.NO_CONTENT:
            return response
