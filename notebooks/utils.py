import json
from typing import List

import pandas as pd
import requests
from schemas.jobs import JobResultDownloadResponse

MODEL_INFO_FILE = "assets/model_info.csv"

EVAL_METRICS = {
    "Meteor": ["meteor", "meteor_mean"],
    "BERT Precision": ["bertscore", "precision_mean"],
    "BERT Recall": ["bertscore", "recall_mean"],
    "BERT F1": ["bertscore", "f1_mean"],
    "ROUGE-1": ["rouge", "rouge1_mean"],
    "ROUGE-2": ["rouge", "rouge2_mean"],
    "ROUGE-L": ["rouge", "rougeL_mean"],
}


def _parse_model_results(result: dict, mi: pd.DataFrame):
    row = {}

    model_name = result["model"]
    row["Model"] = model_name

    for column, metric in EVAL_METRICS.items():
        temp_result = result
        for key in metric:
            value = temp_result.get(key)
            if value is None:
                break
            temp_result = value

        row[column] = value

    row["RAM_GB"] = mi[mi.model_name == model_name]["RAM_GB"].to_numpy()[0]

    return row


def _download_text_file(result: JobResultDownloadResponse) -> str:
    download_url = result.download_url
    download_response = requests.get(download_url)
    return download_response.text


def job_result_download(result: JobResultDownloadResponse) -> str:
    """Download the job results

    Args:
        result (JobResultDownloadResponse): The response object
          containing the results URL.

    Return:
        str: The text content of the downloaded file.
    """
    exp_results = _download_text_file(result)
    return json.loads(exp_results)


def results_to_table(results: List[dict]) -> pd.DataFrame:
    """Visualize results as a table.

    Args:
        results (List[dict]): The content of job results.
    Returns:
        pd.DataFrame: The result table.
    """
    evaluation_results = []

    mi = pd.read_csv(MODEL_INFO_FILE)

    for result in results:
        evaluation_results.append(_parse_model_results(result, mi))

    return pd.DataFrame(evaluation_results)


def get_nested_value(dictionary: dict, path: str, default_value=None) -> str:
    """Get a value from a nested dictionary using a path.

    Args:
        dictionary (dict): The dictionary to search.
        path (str): The path to the value in the dictionary.
        default_value (Any, optional): The value to return if the path is not
          found. Defaults to None.

    Returns:
        str: The value at the path in the dictionary.
    """
    val = dictionary
    for key in path.split("/"):
        val = val.get(key)
        if val is None:
            return default_value
    return val
