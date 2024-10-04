import json
from http import HTTPStatus
from pathlib import Path
from typing import Any, Dict  # noqa: UP035
from uuid import UUID

import requests
from loguru import logger
from requests.exceptions import HTTPError
from schemas.extras import ListingResponse

from mzai.backend.schemas.datasets import DatasetResponse
from mzai.backend.schemas.deployments import DeploymentEvent
from mzai.backend.schemas.experiments import (
    ExperimentCreate,
    ExperimentResponse,
    ExperimentResultDownloadResponse,
    ExperimentResultResponse,
)
from mzai.sdk.healthcheck import HealthCheck

# TODO: move these definitions to an "upper" level to be imported
# by both the SDK client and the backend (the openapi definition
# should be developed first, and then the data classes in both sides
# could be generated)
COMPLETIONS_ROUTE = "completions"
DATASETS_ROUTE = "datasets"
DEPLOYMENTS_ROUTE = "deployments"
HEALTH_ROUTE = "health"
EXPERIMENTS_ROUTE = "experiments"


class LumigatorClient:
    def __init__(self, api_host: str):
        self.api_host = api_host
        # NOTE: do we only support HTTP?
        self._api_url = f"http://{self.api_host}/api/v1"

    def _make_request(
        self,
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

    def __get_response(self, path, verbose: bool = True) -> requests.Response:
        """Makes a request to the specified path and attempts to return the response.
        Raises an exception for any error other than 404 - NOT FOUND.
        """
        try:
            response = self._make_request(path, verbose=verbose)
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

    def post_response(self, path, data=None, verbose: bool = True) -> requests.Response:
        try:
            response = self._make_request(path, data, method="PUT", verbose=verbose)
            if response.status_code == 200:
                return response
        except HTTPError as e:
            if e.response.status_code == 404:
                return e.response
            else:
                # Re-raise the exception if it's not a 404 error
                raise
        except requests.RequestException as e:
            logger.error(f"An error occurred: {e}")
            raise

    def healthcheck(self) -> HealthCheck:
        """Returns healthcheck information."""
        check = HealthCheck()
        response = self.__get_response(str(Path(self._api_url) / HEALTH_ROUTE))
        if response:
            data = response.json()
            check.status = data.get("status")
            check.deployment_type = data.get("deployment_type")

        return check

    def get_datasets(self) -> list[DatasetResponse]:
        response = self.__get_response(str(Path(self._api_url) / DATASETS_ROUTE))

        if not response:
            return []

        return [DatasetResponse(**args) for args in response.json()]

    def get_deployments(self) -> list[DeploymentEvent]:
        response = self.__get_response(str(Path(self._api_url) / HEALTH_ROUTE / DEPLOYMENTS_ROUTE))

        if not response:
            return []

        return [DeploymentEvent(**args) for args in response.json()]


    
    def create_experiment(self, experiment: ExperimentCreate) -> ExperimentResponse:
        """Creates a new experiment."""
        response = self.__post_response(str(Path(self._api_url) / EXPERIMENTS_ROUTE / ''), experiment.model_dump_json())

        if not response:
            return []

        data = response.json()
        return ExperimentResponse(**data)

    def get_experiment(self, experiment_id: UUID) -> ExperimentResponse:
        """Returns information on the experiment for the specified ID."""
        response = self.__get_response(str(Path(self._api_url) / EXPERIMENTS_ROUTE))

        if not response:
            return []

        data = response.json()
        return ExperimentResponse(**data)

    def get_experiments(self, skip: int = 0, limit: int = 100) -> ListingResponse[ExperimentResponse]:
        """Returns information on all experiments."""
        response = self.__get_response(str(Path(self._api_url) / EXPERIMENTS_ROUTE))

        if not response:
            return []

        return [ExperimentResponse(**args) for args in response.json()]

    def get_experiment_result(self, experiment_id: UUID) -> ExperimentResultResponse:
        """Returns the result of the experiment for the specified ID."""
        response = self.__get_response(str(Path(self._api_url) / EXPERIMENTS_ROUTE / f'{experiment_id}' / "result"))

        if not response:
            return []

        data = response.json()
        return ExperimentResultResponse(**data)

    def get_experiment_result_download(self, experiment_id: UUID) -> ExperimentResultDownloadResponse:
        """Returns the result of the experiment for the specified ID."""
        response = self.__get_response(str(Path(self._api_url) / EXPERIMENTS_ROUTE / f'{experiment_id}' / "result" / "download"))

        if not response:
            return []

        data = response.json()
        return ExperimentResultDownloadResponse(**data)
