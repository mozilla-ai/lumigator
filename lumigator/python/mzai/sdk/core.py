from typing import Any, Dict  # noqa: UP035
import json

import requests
from mzai.sdk.healthcheck import HealthCheck

class LumigatorClient():

    def __init__(self, api_host:str):
        self.api_host = api_host
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
                *args,
                **kwargs,  # noqa: B026
            )
            response.raise_for_status()
            print(f'2-> {response}')
            if verbose:
                print(f"{json.dumps(response.json(), indent=2)}")
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            raise
        return response

    def get_response(self, verbose: bool = True)-> requests.Response:
        response = self._make_request(self._api_url, verbose=verbose)
        if response.status_code == 200:
            data = response.json()
            return
        elif response.status_code == 404:
            return
        else:
            print("Either status is not OK or deployment type is not local")
            
    def healthcheck(self)->HealthCheck:
        check = HealthCheck()
        response = self.get_response(self._api_url)
        if response:
            data = response.json()
            check.status = data.get('status')
            check.deployment_type = data.get('deployment_type')

        return response

