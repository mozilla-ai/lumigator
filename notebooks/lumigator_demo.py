"""Common definitions and methods for the lumigator demo notebook."""

import json
from typing import Any, Dict  # noqa: UP035
from uuid import UUID
from pathlib import Path

import requests
import s3fs

# URL where the API can be reached
API_HOST = "localhost"
API_URL = f"http://{API_HOST}/api/v1"

# URL of the Ray server
# (this should not be directly available for the demo)
RAY_SERVER_URL="http://10.144.20.102:8265"

# base S3 path
S3_BASE_PATH="lumigator-storage/experiments/results/"

# ---------------------------------------------------------------------

def make_request(
    url: str,
    method: str = "GET",
    params: Dict[str, Any] = None,  # noqa: UP006
    data: Dict[str, Any] = None,  # noqa: UP006
    files: Dict[str, Any] = None,  # noqa: UP006
    headers: Dict[str, str] = None,  # noqa: UP006
    json_: Dict[str, str] = None,  # noqa: UP006
    timeout: int = 10,
    *args, **kwargs
) -> requests.Response:
    """Make an HTTP request using the requests library.

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
            *args, **kwargs  # noqa: B026
        )
        response.raise_for_status()
        print(f"{json.dumps(response.json(), indent = 2)}")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        raise
    return response

def get_ray_link(job_id: UUID, RAY_SERVER_URL: str) -> str:
    return f"{RAY_SERVER_URL}/#/jobs/{job_id}"

def get_resource_id(response: requests.Response) -> UUID:
    if response.status_code == requests.codes.created:
        return json.loads(response.text).get("id")

def dataset_upload(filename: str) -> requests.Response:
    files = {'dataset': open(filename, 'rb')}
    payload = {'format': 'experiment'}
    r = make_request(f"{API_URL}/datasets", method="POST", data=payload, files=files)
    return r

def dataset_info(dataset_id: UUID) -> requests.Response:
    r = make_request(f"{API_URL}/datasets/{dataset_id}")
    return r

def experiments_submit(
        model_name: str,
        name: str, 
        description: str | None,
        dataset_id: UUID
) -> requests.Response:
    
    payload = {
      "name": name,
      "description": description,
      "model": model_name,
      "dataset": dataset_id,
      "max_samples": 100
    }

    r = make_request(f"{API_URL}/experiments", method="POST", data=json.dumps(payload))
    return r

def experiments_info(experiment_id: UUID) -> requests.Response:
    r = make_request(f"{API_URL}/experiments/{experiment_id}")
    return r

def experiments_result(
        experiment_id: UUID
) -> str:

    exp_info = experiments_info(experiment_id)
    if exp_info.status_code == requests.codes.ok:
        exp_json = json.loads(exp_info.text)
        exp_id = exp_json.get("id")
        exp_name = exp_json.get("name")

        s3_path = Path(S3_BASE_PATH) / exp_name / exp_id / "eval_results.json"

        s3 = s3fs.S3FileSystem()
        with s3.open(s3_path, 'rb') as f:
            results = f.read()
    else:
        results = json.dumps( {"Error": exp_info.status_code} )

    return results

