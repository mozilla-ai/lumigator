import os
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("", []),
        ("   ", []),
        ("http://localhost:3000", ["http://localhost:3000"]),
        (
            "http://localhost:3000,http://localhost:8080",
            ["http://localhost:3000", "http://localhost:8080"],
        ),
        (
            " http://localhost:3000 , http://localhost:8080 ",
            ["http://localhost:3000", "http://localhost:8080"],
        ),
        ("*", ["*"]),
        (
            "http://localhost:3000,*",
            ["*"],
        ),
        (
            " http://localhost:3000,http://localhost:8080,",
            ["http://localhost:3000", "http://localhost:8080"],
        ),
        (
            ",,,",
            [],
        ),
    ],
)
def test_api_allowed_origins(backend_settings, test_input, expected):
    """Ensure that our backend setting for getting CORS allowed origins
    handles being empty, whitespace and when containing one or more entries.
    """
    # Temporarily override the config value that was loaded from env.
    backend_settings._api_cors_allowed_origins = test_input

    result = backend_settings.API_CORS_ALLOWED_ORIGINS
    assert result == expected


@pytest.mark.parametrize(
    "input_env_vars, mock_env_vars, ray_worker_env_vars, expected_result",
    [
        # Test case: No env vars matching expected Ray worker env vars
        ({"VAR1": "value1", "VAR2": "value2"}, {}, ["RAY_WORKER_ENV_VAR3"], {"VAR1": "value1", "VAR2": "value2"}),
        # Test case: Adding new env var which exits in Ray worker env var list
        (
            {"VAR1": "value1", "VAR2": "value2"},
            {"RAY_WORKER_ENV_VAR3": "new_value"},
            ["RAY_WORKER_ENV_VAR3"],
            {"VAR1": "value1", "VAR2": "value2", "RAY_WORKER_ENV_VAR3": "new_value"},
        ),
        # Test case: Overwriting existing env var
        (
            {"VAR1": "value1", "RAY_WORKER_ENV_VAR2": "value2"},
            {"RAY_WORKER_ENV_VAR2": "new_value2"},
            ["RAY_WORKER_ENV_VAR2"],
            {"VAR1": "value1", "RAY_WORKER_ENV_VAR2": "new_value2"},
        ),
        # Test case: No changes if Ray worker env var list is empty
        ({"VAR1": "value1", "VAR2": "value2"}, {}, [], {"VAR1": "value1", "VAR2": "value2"}),
        # Test case: Only Ray worker env var list (and corresponding env vars) exist
        ({}, {"RAY_WORKER_ENV_VAR1": "new_value1"}, ["RAY_WORKER_ENV_VAR1"], {"RAY_WORKER_ENV_VAR1": "new_value1"}),
        # Test case: Multiple variables with the same name in the environment
        (
            {"RAY_WORKER_ENV_VAR1": "value1", "RAY_WORKER_ENV_VAR2": "value2"},
            {"RAY_WORKER_ENV_VAR1": "new_value1", "RAY_WORKER_ENV_VAR2": "new_value2"},
            ["RAY_WORKER_ENV_VAR1", "RAY_WORKER_ENV_VAR2"],
            {"RAY_WORKER_ENV_VAR1": "new_value1", "RAY_WORKER_ENV_VAR2": "new_value2"},
        ),
    ],
)
def test_augment_ray_worker_env_vars(input_env_vars, mock_env_vars, ray_worker_env_vars, expected_result):
    # Mock the environment variables using patch
    with patch.dict(os.environ, mock_env_vars):
        from backend.settings import settings

        # Update the Ray worker environment variables list
        settings.RAY_WORKER_ENV_VARS = ray_worker_env_vars
        # Take a copy of the input before calling the function
        input_copy = input_env_vars.copy()
        result = settings.with_ray_worker_env_vars(input_env_vars)
        assert result == expected_result
        # Ensure the input dictionary is not mutated
        assert input_env_vars == input_copy


def test_backend_project_root():
    """Test to ensure we know the project root."""
    from backend.settings import settings

    # This test should be running from: lumigator/backend/backend/tests/unit
    expected_path = Path(__file__).resolve().parent.parent.parent.parent
    assert settings.PROJECT_ROOT == expected_path


def test_backend_version():
    """Test to ensure we know the current backend version."""
    from backend.settings import settings

    assert settings.VERSION == "0.1.4-alpha"
