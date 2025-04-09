import json
import shutil
from pathlib import Path
from unittest.mock import patch
from uuid import UUID

import numpy as np
import pytest
from datasets import load_dataset
from eval_metrics import EvaluationMetrics
from evaluator import run_eval

from schemas import DatasetConfig, EvalJobConfig, EvaluationConfig


@pytest.fixture
def evaluation_metrics():
    """Create an EvaluationMetrics instance with token_length metric selected."""
    return EvaluationMetrics(["token_length"])


@pytest.fixture
def sample_data():
    """Sample data for testing token length metrics."""
    examples = ["Sample input 1", "Sample input 2"]
    predictions = ["This is a predicted output with several words.", "Another prediction that is fairly short."]
    references = ["This is a reference output with many words to count.", "Another reference with different length."]
    return examples, predictions, references


def test_token_length_calculation(evaluation_metrics, sample_data):
    """Test if token length is calculated correctly."""
    _, predictions, references = sample_data

    result = evaluation_metrics._token_length(predictions, references)

    # Check structure of returned object
    assert "ref_token_length" in result
    assert "pred_token_length" in result
    assert "ref_token_length_mean" in result
    assert "pred_token_length_mean" in result

    # Check types
    assert isinstance(result["ref_token_length"], list)
    assert isinstance(result["pred_token_length"], list)
    assert isinstance(result["ref_token_length_mean"], float)
    assert isinstance(result["pred_token_length_mean"], float)

    # Check values based on the formula len(text.split()) / 0.75
    expected_ref_lengths = [int(len(r.split()) / 0.75) for r in references]
    expected_pred_lengths = [int(len(p.split()) / 0.75) for p in predictions]

    assert result["ref_token_length"] == expected_ref_lengths
    assert result["pred_token_length"] == expected_pred_lengths
    assert result["ref_token_length_mean"] == np.mean(expected_ref_lengths)
    assert result["pred_token_length_mean"] == np.mean(expected_pred_lengths)


def test_token_length_empty_strings(evaluation_metrics):
    """Test token length calculation with empty strings."""
    predictions = ["", "Some text"]
    references = ["", ""]

    result = evaluation_metrics._token_length(predictions, references)

    assert result["ref_token_length"] == [0, 0]
    assert result["pred_token_length"] == [0, int(len("Some text".split()) / 0.75)]
    assert result["ref_token_length_mean"] == 0.0
    assert result["pred_token_length_mean"] == result["pred_token_length"][1] / 2


def test_empty_fields_cast_as_float64():
    test_path_csv = Path("../../sample_data/summarization/predictions_gibberish.csv")
    test_path = test_path_csv.with_suffix("")
    csv = load_dataset("csv", data_files=str(test_path_csv), split="train")
    csv.save_to_disk(test_path)
    non_existing_id = UUID("d34dbeef-4bea-4d19-ad06-214202165812")
    eval = EvalJobConfig(
        name="test",
        dataset=DatasetConfig(path=str(test_path)),
        evaluation=EvaluationConfig(metrics=["rouge"], storage_path="/tmp/test_empty_fields_cast_as_float64.metrics"),
    )
    run_eval(eval, non_existing_id)
    shutil.rmtree(test_path)


@patch("eval_metrics.EvaluationMetrics._g_eval_measure_with_retry")
def test_geval_metrics_dict(mock_geval):
    """Verifies that all geval-based metrics appear in the outputs.

    When a new geval_based metric is added to evaluator, eval outputs change according
    to informations stored in three different places:

    - `g_eval_prompts.json`, which contains sub_metric names (e.g. coherence, fluency, etc)
       and a mapping from tasks to task-specific prompts.
    - `EvaluationMetrics._supported_metrics` in `eval_metrics`, to map the new metric
       name with a specific task (and possible extra params).
    - `EvalJobMetrics` in `schemas` which specifies the format of the new evaluation
       results and where they will appear in the resulting dictionary.

    This test automatically verifies, for each metric called geval_*, that there is
    actually an output with the same name inside the resulting dictionary.
    """
    # we cannot access _supported_metrics statically, so we instantiate
    # the EvaluationMetrics class with a known metric
    em = EvaluationMetrics(["g_eval_summarization"])
    # get the list of supported metrics, and instantiate the EvaluationMetrics
    # class again with all the g_eval* ones
    g_eval_metrics = [x for x in em._supported_metrics if x.startswith("g_eval")]
    em = EvaluationMetrics(g_eval_metrics)

    # run all g_eval* evaluations (mocked) to obtain the output dictionary
    mock_geval.return_value = {"score": np.random.rand(), "reason": "Because I said so"}
    results = em.run_all(
        examples=["Ceci n'est pas un pipe"],
        pred=["This is not a pipe"],
        ref=["This is not a pipe"],
    )

    # check that all g_eval metrics are present in the output dictionary
    for metric_name in g_eval_metrics:
        assert metric_name in results.model_dump()
