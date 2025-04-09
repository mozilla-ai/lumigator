import pytest
from lumigator_schemas.tasks import Metric, TaskType, get_metrics_for_task


def test_default_metrics_covers_all_task_types():
    # Ensure all task types have metrics associated with them.
    for task_type in TaskType:
        try:
            metrics = get_metrics_for_task(task_type)
            assert metrics, f"No metrics for task type '{task_type}'"
        except KeyError as e:
            pytest.fail(str(e))


def test_default_metrics_by_task():
    # Check that the metrics for each task are correct, if new tasks are added then
    # 'test_default_metrics_covers_all_task_types' should fail and this test should
    # be updated to reflect the new task and its metrics.
    assert get_metrics_for_task(TaskType.SUMMARIZATION) == {
        Metric.BERTSCORE,
        Metric.METEOR,
        Metric.ROUGE,
    }
    assert get_metrics_for_task(TaskType.TRANSLATION) == {
        Metric.BLEU,
        Metric.COMET,
        Metric.METEOR,
    }
    assert get_metrics_for_task(TaskType.TEXT_GENERATION) == {
        Metric.BERTSCORE,
        Metric.BLEU,
        Metric.METEOR,
        Metric.ROUGE,
    }
