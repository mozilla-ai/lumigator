"""Common definitions and methods for the lumigator demo notebook."""

import json
import os
from pathlib import Path
from typing import Any, Dict  # noqa: UP035
from uuid import UUID

import pandas as pd
import requests

# URL where the API can be reached
API_HOST = os.environ['LUMIGATOR_SERVICE_HOST']
API_URL = f"http://{API_HOST}/api/v1"

# URL of the Ray server
# (this should not be directly available for the demo)
RAY_HEAD_HOST = os.environ['RAYCLUSTER_KUBERAY_HEAD_SVC_PORT_8265_TCP_ADDR']
RAY_SERVER_URL = f"http://{RAY_HEAD_HOST}:8265"

# base S3 path
S3_BASE_PATH="lumigator-storage/experiments/results/"

# - BASE --------------------------------------------------------------

def make_request(
    url: str,
    method: str = "GET",
    params: Dict[str, Any] = None,  # noqa: UP006
    data: Dict[str, Any] = None,  # noqa: UP006
    files: Dict[str, Any] = None,  # noqa: UP006
    headers: Dict[str, str] = None,  # noqa: UP006
    json_: Dict[str, str] = None,  # noqa: UP006
    timeout: int = 10,
    verbose: bool = True,
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
        if verbose:
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

# - DATASETS ----------------------------------------------------------

def dataset_upload(filename: str) -> requests.Response:
    with Path(filename).open("rb") as f:
        files = {'dataset': f}
        payload = {'format': 'experiment'}
        r = make_request(f"{API_URL}/datasets", method="POST", data=payload, files=files)
    return r

def dataset_info(dataset_id: UUID) -> requests.Response:
    r = make_request(f"{API_URL}/datasets/{dataset_id}")
    return r

# - EXPERIMENTS -------------------------------------------------------

def experiments_submit(
        model_name: str,
        name: str, 
        description: str | None,
        dataset_id: UUID,
        max_samples: int = 10
) -> requests.Response:
    
    payload = {
      "name": name,
      "description": description,
      "model": model_name,
      "dataset": dataset_id,
      "max_samples": max_samples
    }

    r = make_request(f"{API_URL}/experiments", method="POST", data=json.dumps(payload))
    return r

def experiments_info(experiment_id: UUID) -> requests.Response:
    r = make_request(f"{API_URL}/experiments/{experiment_id}")
    return r

# - RESULTS -----------------------------------------------------------

def experiments_result_download(
        experiment_id: UUID
) -> str:
    r = make_request(f"{API_URL}/experiments/{experiment_id}/result/download", verbose=False)
    download_url = json.loads(r.text)['download_url']
    # boto3 returns download URLs with default port, CW does not have it
    # (this is ugly but does not affect local or AWS setups)
    download_url = download_url.replace("object.lga1.coreweave.com:4566",
                                        "object.lga1.coreweave.com")

    download_response = make_request(download_url, verbose=False)
    exp_results = json.loads(download_response.text)
    return exp_results


def eval_results_to_table(models, eval_results):
    """Format evaluation results jsons into one pandas dataframe."""
    # metrics dict format is
    # "column name": [list of keys to get val in nested results dict]
    metrics = {
        "Meteor": ["meteor", "meteor_mean"],
        "BERT Precision": ["bertscore", "precision_mean"],
        "BERT Recall": ["bertscore", "recall_mean"],
        "BERT F1": ["bertscore", "f1_mean"],
        "ROUGE-1": ["rouge", "rouge1_mean"],
        "ROUGE-2": ["rouge", "rouge2_mean"],
        "ROUGE-L": ["rouge", "rougeL_mean"],
    }

    def parse_model_results(model, results):
        row = {}
        row["Model"] = model.replace("hf://", "")

        for column, metric in metrics.items():
            temp_results = results
            for key in metric:
                value = temp_results.get(key)
                if value is None:
                    break
                temp_results = value

            row[column] = value
        return row

    eval_table = []
    for model, results in zip(models, eval_results, strict=True):
        eval_table.append(parse_model_results(model, results))

    return pd.DataFrame(eval_table)