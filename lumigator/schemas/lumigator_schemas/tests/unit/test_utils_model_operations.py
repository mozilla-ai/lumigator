from typing import Any

import pytest
from lumigator_schemas.jobs import JobResultObject
from lumigator_schemas.utils.model_operations import deep_merge_dicts, merge_models
from pydantic import BaseModel


class TestModel(BaseModel):
    name: str
    metadata: dict[str, Any] | None = None


@pytest.mark.parametrize(
    "base_model, overlay_model, deep_merge, expected_merged, expected_overwritten",
    [
        # Case 1: base_model is None, overlay_model is provided
        (
            None,
            TestModel(name="overlay", metadata={"key": "value"}),
            False,
            TestModel(name="overlay", metadata={"key": "value"}),
            set(),
        ),
        # Case 2: overlay_model is None, base_model is provided
        (
            TestModel(name="base", metadata={"key": "base_value"}),
            None,
            False,
            TestModel(name="base", metadata={"key": "base_value"}),
            set(),
        ),
        # Case 3: Base and Overlay models are provided, shallow merge (no deep merge)
        (
            TestModel(name="base", metadata={"key": "base_value"}),
            TestModel(name="overlay", metadata={"key": "overlay_value"}),
            False,
            TestModel(name="overlay", metadata={"key": "overlay_value"}),
            {"name", "metadata"},
        ),
        # Case 4: Base and Overlay models are provided, shallow merge (no deep merge)
        (
            TestModel(name="base", metadata={"key": "base_value"}),
            TestModel(name="overlay", metadata={"key": "base_value"}),
            False,
            TestModel(name="overlay", metadata={"key": "base_value"}),
            {"name"},
        ),
        # Case 5: Base and Overlay models are provided, deep merge (nested dictionaries)
        (
            TestModel(name="base", metadata={"key": {"subkey": "base_value"}}),
            TestModel(name="overlay", metadata={"key": {"subkey": "overlay_value"}}),
            True,
            TestModel(name="overlay", metadata={"key": {"subkey": "overlay_value"}}),
            {"name", "metadata.key.subkey"},
        ),
    ],
)
def test_merge_models(base_model, overlay_model, deep_merge, expected_merged, expected_overwritten):
    merged_model, overwritten_keys = merge_models(base_model, overlay_model, deep_merge)

    assert merged_model == expected_merged
    assert overwritten_keys == expected_overwritten


@pytest.mark.parametrize(
    "base_dict, overlay_dict, deep_merge, expected_merged, expected_overwritten",
    [
        # Case 1: Shallow merge (no recursion)
        ({"key": "base_value"}, {"key": "overlay_value"}, False, {"key": "overlay_value"}, {"key"}),
        # Case 2: Deep merge (nested dictionaries)
        (
            {"key": {"subkey": "base_value"}},
            {"key": {"subkey": "overlay_value"}},
            True,
            {"key": {"subkey": "overlay_value"}},
            {"key.subkey"},
        ),
        # Case 3: Overwriting a top-level key (non-nested)
        ({"key": "base_value"}, {"key": "overlay_value"}, False, {"key": "overlay_value"}, {"key"}),
        # Case 4: Overwriting a nested key (deep merge)
        (
            {"key": {"subkey": "base_value"}},
            {"key": {"subkey": "overlay_value"}},
            True,
            {"key": {"subkey": "overlay_value"}},
            {"key.subkey"},
        ),
        # Case 5: No overlay values, so base_dict remains the same
        ({"key": "base_value"}, {}, False, {"key": "base_value"}, set()),
    ],
)
def test_deep_merge_dicts(base_dict, overlay_dict, deep_merge, expected_merged, expected_overwritten):
    merged_dict, overwritten_keys = deep_merge_dicts(base_dict, overlay_dict, deep_merge)

    assert merged_dict == expected_merged
    assert overwritten_keys == expected_overwritten


@pytest.mark.parametrize(
    "a, b, expected_overwritten_keys",
    [
        (
            "json_workflow_results",
            "json_workflow_results_overlay_all",
            {"parameters", "metrics", "artifacts"},
        ),
        (
            "json_workflow_results",
            "json_workflow_results_overlay_artifacts_same",
            {"parameters", "metrics"},
        ),
    ],
)
def test_merge_job_results(a, b, expected_overwritten_keys, request):
    # Create JobResultObjects from the JSON data
    job_result_1 = JobResultObject(**request.getfixturevalue(a))
    job_result_2 = JobResultObject(**request.getfixturevalue(b))

    # Merge the models using your merge_models function
    merged_model, overwritten_keys = merge_models(job_result_1, job_result_2, deep_merge=False)

    # Assert the merged model is as expected
    bertscore = merged_model.metrics.get("bertscore", {})
    assert bertscore != {}
    bertscore_precision = bertscore.get("precision", [])
    assert len(bertscore_precision) > 0
    assert bertscore_precision[0] == 0.2
    bertscore_hashcode = bertscore.get("hashcode", "")
    assert bertscore_hashcode == "ROBOTO-large_L17_no-idf_version=0.3.12(hug_trans=4.48.0)"
    assert merged_model.parameters.get("name", "") == "test2-evaluation/b5700c88-57b5-42d7-a128-aedaf4338117"
    meteor = merged_model.metrics.get("meteor", {})
    assert meteor != {}
    meteor_meteor = meteor.get("meteor", [])
    assert len(meteor_meteor) > 0
    assert meteor_meteor[0] == 0.555

    # Assert the overwritten keys are as expected
    assert overwritten_keys == expected_overwritten_keys
