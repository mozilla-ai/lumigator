import numpy as np
import pytest
from eval_metrics import EvaluationMetrics


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
