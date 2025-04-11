import pytest
from inference import _calculate_average_metrics

from schemas import AverageInferenceMetrics, InferenceMetrics, PredictionResult


def _make_result_with_metrics(
    prediction: str = "test",
    reasoning: str = None,
    prompt=10,
    total=20,
    completion=5,
    reasoning_tokens=3,
    answer=2,
):
    return PredictionResult(
        prediction=prediction,
        reasoning=reasoning,
        metrics=InferenceMetrics(
            prompt_tokens=prompt,
            total_tokens=total,
            completion_tokens=completion,
            reasoning_tokens=reasoning_tokens,
            answer_tokens=answer,
        ),
    )


def _make_result_without_metrics(prediction: str = "test", reasoning: str = None):
    return PredictionResult(
        prediction=prediction,
        reasoning=reasoning,
        metrics=None,
    )


class TestCalculateAverageMetrics:
    def test_returns_average_when_all_have_metrics(self):
        results = [
            _make_result_with_metrics(prompt=10, total=20, completion=5, reasoning_tokens=3, answer=2),
            _make_result_with_metrics(prompt=30, total=40, completion=15, reasoning_tokens=9, answer=6),
        ]

        avg = _calculate_average_metrics(results)

        assert isinstance(avg, AverageInferenceMetrics)
        assert avg.avg_prompt_tokens == 20.0
        assert avg.avg_total_tokens == 30.0
        assert avg.avg_completion_tokens == 10.0
        assert avg.avg_reasoning_tokens == 6.0
        assert avg.avg_answer_tokens == 4.0

    def test_returns_none_when_none_have_metrics(self):
        results = [
            _make_result_without_metrics(),
            _make_result_without_metrics(),
        ]

        assert _calculate_average_metrics(results) is None

    def test_raises_when_some_have_metrics_and_some_dont(self):
        results = [
            _make_result_with_metrics(),
            _make_result_without_metrics(),
        ]

        with pytest.raises(ValueError, match="Prediction result 'metrics' must be present in ALL results or NONE"):
            _calculate_average_metrics(results)

    def test_handles_empty_list(self):
        assert _calculate_average_metrics([]) is None
