import pytest
from lumigator_schemas.experiments import ExperimentCreate
from lumigator_schemas.tasks import TaskType
from pydantic import ValidationError


@pytest.mark.parametrize(
    "task, source_language, target_language, should_pass, error_msg",
    [
        (TaskType.SUMMARIZATION, None, None, True, None),
        (
            TaskType.SUMMARIZATION,
            "en",
            None,
            False,
            "Fields source_language and target_language should not be provided",
        ),
        (
            TaskType.SUMMARIZATION,
            None,
            "fr",
            False,
            "Fields source_language and target_language should not be provided",
        ),
        (TaskType.TRANSLATION, "en", "fr", True, None),
        (
            TaskType.TRANSLATION,
            None,
            None,
            False,
            "Both source_language and target_language must be provided",
        ),
        (
            TaskType.TRANSLATION,
            "en",
            None,
            False,
            "Both source_language and target_language must be provided",
        ),
        (
            TaskType.TRANSLATION,
            None,
            "fr",
            False,
            "Both source_language and target_language must be provided",
        ),
    ],
)
def test_experiment_create_task_validation(task, source_language, target_language, should_pass, error_msg):
    # Base required fields with dummy dataset UUID
    base_config = {
        "name": "test-experiment",
        "description": "Validation test",
        "dataset": "d34dd34d-d34d-d34d-d34d-d34dd34dd34d",
        "task_definition": {"task": task, "source_language": source_language, "target_language": target_language},
    }

    # Add language fields if specified
    if source_language is not None:
        base_config["source_language"] = source_language
    if target_language is not None:
        base_config["target_language"] = target_language

    if should_pass:
        # Should create successfully
        ExperimentCreate(**base_config)
    else:
        with pytest.raises(ValidationError) as exc_info:
            ExperimentCreate(**base_config)

        # Verify error message contains expected text
        assert error_msg in str(exc_info.value)
