"""Common definitions and methods for the lumigator demo notebook."""

import io
import json
import os
from pathlib import Path
from typing import Any, Dict  # noqa: UP035
from uuid import UUID

import numpy as np
import pandas as pd
import requests

# APP URL
API_HOST = os.environ["LUMIGATOR_SERVICE_HOST"]
API_URL = f"http://{API_HOST}/api/v1"

# Ray URL
RAY_HEAD_HOST = os.environ["RAYCLUSTER_KUBERAY_HEAD_SVC_PORT_8265_TCP_ADDR"]
RAY_SERVER_URL = f"http://{RAY_HEAD_HOST}:8265"

# base S3 path
S3_BASE_PATH = "lumigator-storage/experiments/results/"


# EVAL_METRICS is a dict we use to show / refer to eval metrics
# in pandas dataframes and when filtering by metric name.
# The dict format is
# "column name": [list of keys to get val in nested results dict]
EVAL_METRICS = {
    "Meteor": ["meteor", "meteor_mean"],
    "BERT Precision": ["bertscore", "precision_mean"],
    "BERT Recall": ["bertscore", "recall_mean"],
    "BERT F1": ["bertscore", "f1_mean"],
    "ROUGE-1": ["rouge", "rouge1_mean"],
    "ROUGE-2": ["rouge", "rouge2_mean"],
    "ROUGE-L": ["rouge", "rougeL_mean"],
}

# the following file contains information about different models
# (currently just max RAM consumption on the TB inference task)
MODEL_INFO_FILE = "assets/model_info.csv"

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
    *args,
    **kwargs,
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
            *args,
            **kwargs,  # noqa: B026
        )
        response.raise_for_status()
        if verbose:
            print(f"{json.dumps(response.json(), indent = 2)}")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        raise
    return response

def get_nested_value(dictionary: dict, path: str, default_value=None) -> str:
    val = dictionary
    for key in path.split("/"):
        val = val.get(key)
        if val is None:
            return default_value
    return val

def get_ray_link(job_id: UUID, RAY_SERVER_URL: str) -> str:
    return f"{RAY_SERVER_URL}/#/jobs/{job_id}"


def get_resource_id(response: requests.Response) -> UUID:
    if response.status_code == requests.codes.created:
        return json.loads(response.text).get("id")


def get_job_status(response: requests.Response) -> UUID:
    if response.status_code == requests.codes.ok:
        return json.loads(response.text).get("status")


def download_text_file(response: requests.Response) -> str:
    """Downloads a text file from the API.

    Given a response from an API `/download` URL, returns the
    corresponding text file.
    Can be used both for textual datasets and evaluation results/logs.
    """
    download_url = json.loads(response.text)["download_url"]
    download_response = make_request(download_url, verbose=False)
    return download_response.text


# - DATASETS ----------------------------------------------------------


def dataset_upload(filename: str) -> requests.Response:
    with Path(filename).open("rb") as f:
        files = {"dataset": f}
        payload = {"format": "experiment"}
        response = make_request(
            f"{API_URL}/datasets", method="POST", data=payload, files=files
        )
    return response


def dataset_info(dataset_id: UUID) -> requests.Response:
    response = make_request(f"{API_URL}/datasets/{dataset_id}")
    return response

def get_datasets() -> requests.Response:
    response = make_request(f"{API_URL}/datasets/")
    return response

def dataset_download(dataset_id: UUID) -> pd.DataFrame:
    """Downloads a CSV dataset from the backend and returns a pandas df.

    NOTE: currently limited to CSV (single-file) datasets, to be extended
          with more general dataset types (e.g. HF datasets as we already
          support their upload).
    """
    response = make_request(f"{API_URL}/datasets/{dataset_id}/download", verbose=False)
    csv_dataset = download_text_file(response)
    return pd.read_csv(io.StringIO(csv_dataset))


# - EXPERIMENTS -------------------------------------------------------


def experiments_submit(
    model_name: str,
    name: str,
    description: str | None,
    dataset_id: UUID,
    max_samples: int | None = None,
    system_prompt: str | None = None,
) -> requests.Response:
    if system_prompt is None and (
        model_name.startswith("oai://") or model_name.startswith("http://")
    ):
        system_prompt = "You are a helpful assistant, expert in text summarization. For every prompt you receive, provide a summary of its contents in at most two sentences."  # noqa: E501

    payload = {
        "name": name,
        "description": description,
        "model": model_name,
        "dataset": dataset_id,
        "max_samples": max_samples,
        "system_prompt": system_prompt,
    }

    response = make_request(f"{API_URL}/experiments", method="POST", data=json.dumps(payload))
    return response


def experiments_info(experiment_id: UUID) -> requests.Response:
    response = make_request(f"{API_URL}/experiments/{experiment_id}")
    return response


def experiments_status(experiment_id: UUID) -> str:
    response = make_request(f"{API_URL}/health/jobs/{experiment_id}", verbose=False)
    return get_job_status(response)


def show_experiment_statuses(job_ids):
    still_running = False
    for job_id in job_ids:
        job_status = experiments_status(job_id)
        print(f"{job_id}: {job_status}")
        if job_status == "PENDING" or job_status == "RUNNING":
            still_running = True
    return still_running


# - RESULTS -----------------------------------------------------------


def experiments_result_download(experiment_id: UUID) -> str:
    response = make_request(
        f"{API_URL}/experiments/{experiment_id}/result/download", verbose=False
    )
    exp_results = json.loads(download_text_file(response))
    return exp_results

def eval_results_to_table(eval_results):
    mi = pd.read_csv(MODEL_INFO_FILE)

    """Format evaluation results jsons into one pandas dataframe."""
    def parse_model_results(results):
        row = {}

        model_name = results['model']
        row["Model"] = model_name

        for column, metric in EVAL_METRICS.items():
            temp_results = results
            for key in metric:
                value = temp_results.get(key)
                if value is None:
                    break
                temp_results = value

            row[column] = value

        row["RAM_GB"] = mi[mi.model_name == model_name]['RAM_GB'].values[0]

        return row

    eval_table = []
    for results in eval_results:
        eval_table.append(parse_model_results(results))

    return pd.DataFrame(eval_table)


def runs_to_eval_table(job_ids):
    eval_results = []
    for job_id in job_ids:
        eval_results.append(experiments_result_download(job_id))

    # return results as a pandas dataframe
    return eval_results_to_table(eval_results)


def show_best_worst(job_ids, model_name, metric_name):
    """Shows best and worst results for a given model and metric."""
    found = 0
    for job_id in job_ids:
        result = experiments_result_download(job_id)
        if result['model'].endswith(model_name):
            found = 1
            break

    if not found:
        print(f"I could not find {model_name} between these jobs")

    # look into result following the metric_name path
    # defined in EVAL_METRICS
    metric_vals = result

    for k in metric_name.split("/"):
        metric_vals = metric_vals[k]

    worst_best_idx = [np.argmin(metric_vals), np.argmax(metric_vals)]

    return pd.DataFrame(zip(
        np.array(result['examples'])[worst_best_idx],
        np.array(result['ground_truth'])[worst_best_idx],
        np.array(result['predictions'])[worst_best_idx],
        np.array(metric_vals)[worst_best_idx]
        ), columns=['original', 'GT', 'prediction', metric_name]
    )

# - GROUND TRUTH -----------------------------------------------------------


def create_deployment(gpus: float, replicas: float) -> str:
    data = {"num_gpus": gpus, "num_replicas": replicas}
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    response = make_request(
        f"{API_URL}/ground-truth/deployments",
        headers=headers,
        data=json.dumps(data),
        method="POST",
    )
    return json.loads(response.text).get("id")

def get_deployments(verbose: bool = True) -> requests.Response:
    response = make_request(f"{API_URL}/ground-truth/deployments/", verbose=verbose)
    return response

def get_deployment_status(verbose: bool = True) -> requests.Response:
    response = make_request(f"{API_URL}/health/deployments", verbose=verbose)
    return response

def get_summarizer_deployment_id():
    """Gets the summarizer deployment id from ray serve."""
    path = "applications/summarizer/deployed_app_config/args/description"
    r = get_deployment_status(verbose=False)
    return get_nested_value(json.loads(r.text), path)

def delete_deployment(deployment_id:UUID) -> requests.Response:
    response = make_request(
        f"{API_URL}/ground-truth/deployments/{deployment_id}",
        method="DELETE",
        verbose=False
    )
    return response

def get_bart_ground_truth(deployment_id: UUID, prompt: str) -> dict:

    data = {'text': prompt}

    response = make_request(
        f"{API_URL}/ground-truth/deployments/{deployment_id}",
        method="POST",
        data=json.dumps(data),
        verbose=False
    )
    return response

def get_mistral_ground_truth(prompt: str) -> dict:
    response = make_request(
        f"{API_URL}/completions/mistral",
        method="POST",
        data=json.dumps({"text": prompt}),
        verbose=False
    )
    data_dict = json.loads(response.text)
    return data_dict
