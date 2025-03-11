import uuid

import pytest
from lumigator_schemas.transforms.job_submission_response_transform import (
    _extract_dataset,
    _extract_json_token,
    _extract_max_samples,
    _extract_model_name_or_path,
    transform_job_submission_response,
)


@pytest.mark.parametrize(
    "input_data, expected",
    [
        # Valid entrypoint with proper JSON config
        (
            {
                "entrypoint": 'python evaluator.py --config \'{"name":"1-evaluation/7979add1-d5a7-493a-90a8-e4d170c87174","dataset":{"path":"s3://lumigator-storage/datasets/577af11d-0808-4c56-bb47-5fb2cb4324b1/sample_translation_en_de-annotated.csv"},"evaluation":{"metrics":["rouge","meteor","bertscore","bleu"],"max_samples":1,"return_input_data":true,"return_predictions":true,"storage_path":"s3://lumigator-storage/jobs/results/"}}\''
            },
            {
                "entrypoint": 'python evaluator.py --config \'{"name":"1-evaluation/7979add1-d5a7-493a-90a8-e4d170c87174","dataset":{"path":"s3://lumigator-storage/datasets/577af11d-0808-4c56-bb47-5fb2cb4324b1/sample_translation_en_de-annotated.csv"},"evaluation":{"metrics":["rouge","meteor","bertscore","bleu"],"max_samples":1,"return_input_data":true,"return_predictions":true,"storage_path":"s3://lumigator-storage/jobs/results/"}}\'',
                "config": {
                    "name": "1-evaluation/7979add1-d5a7-493a-90a8-e4d170c87174",
                    "dataset": {
                        "id": uuid.UUID("577af11d-0808-4c56-bb47-5fb2cb4324b1"),
                        "name": "sample_translation_en_de-annotated.csv",
                    },
                    "evaluation": {
                        "metrics": ["rouge", "meteor", "bertscore", "bleu"],
                        "max_samples": 1,
                        "return_input_data": True,
                        "return_predictions": True,
                        "storage_path": "s3://lumigator-storage/jobs/results/",
                    },
                    "max_samples": 1,
                    "model_name_or_path": None,
                },
            },
        ),
        # Invalid entrypoint (not a string)
        ({"entrypoint": 12345}, {"entrypoint": 12345}),
        # Missing entrypoint
        ({}, {}),
        # Valid entrypoint with invalid JSON config
        (
            {
                "entrypoint": 'python evaluator.py --config \'{"name":"1-evaluation/7979add1-d5a7-493a-90a8-e4d170c87174","dataset":{"path":"s3://lumigator-storage/datasets/577af11d-0808-4c56-bb47-5fb2cb4324b1/sample_translation_en_de-annotated.csv"},"evaluation":{"metrics":["rouge","meteor","bertscore","bleu"],"max_samples":1,"return_input_data":true,"return_predictions":true,"storage_path":"s3://lumigator-storage/jobs/results/"\''
            },
            {
                "entrypoint": 'python evaluator.py --config \'{"name":"1-evaluation/7979add1-d5a7-493a-90a8-e4d170c87174","dataset":{"path":"s3://lumigator-storage/datasets/577af11d-0808-4c56-bb47-5fb2cb4324b1/sample_translation_en_de-annotated.csv"},"evaluation":{"metrics":["rouge","meteor","bertscore","bleu"],"max_samples":1,"return_input_data":true,"return_predictions":true,"storage_path":"s3://lumigator-storage/jobs/results/"\''
            },
        ),
        # Valid entrypoint with no config flag
        ({"entrypoint": "python evaluator.py --no-config"}, {"entrypoint": "python evaluator.py --no-config"}),
    ],
)
def test_transform_job_submission_response(input_data, expected):
    result = transform_job_submission_response(input_data)
    assert result == expected


@pytest.mark.parametrize(
    "tokens, flag, expected",
    [
        (["--config", '{"key": "value"}'], "--config", {"key": "value"}),  # Valid JSON
        (["--config", '\'{"key": "value"}\''], "--config", {"key": "value"}),  # Valid JSON with single quotes
        (["--config", '{"key": "value"'], "--config", None),  # Invalid JSON
        (["--other", '{"key": "value"}'], "--config", None),  # Missing flag
        ([], "--config", None),  # Empty tokens list
        (["--config"], "--config", None),  # Flag with no JSON
        (["--config", ""], "--config", None),  # Flag with empty string
        (["--config", "'"], "--config", None),  # Flag with single quote
        (["--config", "''"], "--config", None),  # Flag with empty single quotes
        (
            [
                "--config",
                '{"name":"1-evaluation/7979add1-d5a7-493a-90a8-e4d170c87174","dataset":{"path":"s3://lumigator-storage/datasets/577af11d-0808-4c56-bb47-5fb2cb4324b1/sample_translation_en_de-annotated.csv"},"evaluation":{"metrics":["rouge","meteor","bertscore","bleu"],"max_samples":1,"return_input_data":true,"return_predictions":true,"storage_path":"s3://lumigator-storage/jobs/results/"}}',
            ],
            "--config",
            {
                "name": "1-evaluation/7979add1-d5a7-493a-90a8-e4d170c87174",
                "dataset": {
                    "path": "s3://lumigator-storage/datasets/577af11d-0808-4c56-bb47-5fb2cb4324b1/sample_translation_en_de-annotated.csv"
                },
                "evaluation": {
                    "metrics": ["rouge", "meteor", "bertscore", "bleu"],
                    "max_samples": 1,
                    "return_input_data": True,
                    "return_predictions": True,
                    "storage_path": "s3://lumigator-storage/jobs/results/",
                },
            },
        ),
        # Valid JSON for evaluator
        (
            [
                "--config",
                '{"name":"1-inference/7fa242e9-25d6-4088-9492-47bc803cf32f","dataset":{"path":"s3://lumigator-storage/datasets/97940b79-4e23-4235-9a86-f4c560ecc724/sample_translation_en_de.csv"},"job":{"max_samples":1,"storage_path":"s3://lumigator-storage/jobs/results/","output_field":"predictions","enable_tqdm":true},"system_prompt":"translate en to de:","inference_server":{"base_url":null,"model":"gpt-4o-mini","provider":"openai","max_retries":3},"generation_config":{"max_new_tokens":1024,"frequency_penalty":0.0,"temperature":1.0,"top_p":1.0},"hf_pipeline":null}',
            ],
            "--config",
            {
                "name": "1-inference/7fa242e9-25d6-4088-9492-47bc803cf32f",
                "dataset": {
                    "path": "s3://lumigator-storage/datasets/97940b79-4e23-4235-9a86-f4c560ecc724/sample_translation_en_de.csv"
                },
                "job": {
                    "max_samples": 1,
                    "storage_path": "s3://lumigator-storage/jobs/results/",
                    "output_field": "predictions",
                    "enable_tqdm": True,
                },
                "system_prompt": "translate en to de:",
                "inference_server": {"base_url": None, "model": "gpt-4o-mini", "provider": "openai", "max_retries": 3},
                "generation_config": {
                    "max_new_tokens": 1024,
                    "frequency_penalty": 0.0,
                    "temperature": 1.0,
                    "top_p": 1.0,
                },
                "hf_pipeline": None,
            },
        ),  # Valid JSON for inference
    ],
)
def test_extract_json_token(tokens, flag, expected):
    result = _extract_json_token(tokens, flag)
    assert result == expected


@pytest.mark.parametrize(
    "config_dict, expected",
    [
        # Valid dataset path
        (
            {"dataset": {"path": "s3://lumigator-storage/datasets/123e4567-e89b-12d3-a456-426614174000/sample.csv"}},
            {"id": uuid.UUID("123e4567-e89b-12d3-a456-426614174000"), "name": "sample.csv"},
        ),
        # Missing dataset path
        ({"dataset": {}}, pytest.raises(ValueError, match="Unable to parse dataset path from entrypoint config")),
        # Invalid dataset path (no UUID)
        (
            {"dataset": {"path": "s3://lumigator-storage/datasets/sample.csv"}},
            pytest.raises(ValueError, match="Could not extract dataset ID and file name from path"),
        ),
        # Empty config dictionary
        ({}, pytest.raises(ValueError, match="Unable to parse dataset, missing entrypoint config")),
        # Empty config dictionary
        (None, pytest.raises(ValueError, match="Unable to parse dataset, missing entrypoint config")),
    ],
)
def test_extract_dataset(config_dict, expected):
    if isinstance(expected, dict):
        result = _extract_dataset(config_dict)
        assert result == expected
    else:
        with expected:
            _extract_dataset(config_dict)


@pytest.mark.parametrize(
    "config_dict, expected",
    [
        ({"model": {"path": "model/path"}}, "model/path"),
        ({"model": {"inference": {"model": "model/inference/path"}}}, "model/inference/path"),
        ({"hf_pipeline": {"model_name_or_path": "hf_pipeline/model/path"}}, "hf_pipeline/model/path"),
        ({"inference_server": {"model": "inference_server/model/path"}}, "inference_server/model/path"),
        ({"model": None}, None),
        ({"model": {"path": None}}, None),
        ({"model": {"inference": None}}, None),
        ({"model": {"inference": {"model": None}}}, None),
        ({"hf_pipeline": None}, None),
        ({"inference_server": None}, None),
        ({}, None),
        (None, None),
        ({"model": {}, "hf_pipeline": {}, "inference_server": {}}, None),
    ],
)
def test_extract_model_name_or_path(config_dict, expected):
    result = _extract_model_name_or_path(config_dict)
    assert result == expected


@pytest.mark.parametrize(
    "config_dict, expected",
    [
        # Valid max_samples in job
        ({"job": {"max_samples": 10}}, 10),
        # Valid max_samples in evaluation
        ({"evaluation": {"max_samples": 5}}, 5),
        # max_samples in both job and evaluation (job takes precedence)
        ({"job": {"max_samples": 10}, "evaluation": {"max_samples": 5}}, 10),
        # Missing max_samples
        ({}, pytest.raises(ValueError, match="Unable to parse  max_samples, missing entrypoint config")),
        # no config
        (None, pytest.raises(ValueError, match="Unable to parse  max_samples, missing entrypoint config")),
        # max_samples not in job or evaluation
        (
            {"job": {}, "evaluation": {}},
            pytest.raises(ValueError, match="Unable to parse max_samples from entrypoint config"),
        ),
    ],
)
def test_extract_max_samples(config_dict, expected):
    if isinstance(expected, int):
        result = _extract_max_samples(config_dict)
        assert result == expected
    else:
        with expected:
            _extract_max_samples(config_dict)
