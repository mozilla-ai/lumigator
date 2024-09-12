import os
from unittest import mock

import pytest
from pydantic import ValidationError

from lm_buddy.configs.wandb import WandbRunConfig
from tests.test_utils import copy_pydantic_json


@pytest.fixture
def mock_environment_without_keys():
    """Mocks an environment missing common API keys."""
    with mock.patch.dict(os.environ, clear=True):
        yield


@pytest.fixture
def wandb_run_config():
    return WandbRunConfig(
        id="run-id",
        project="research",
        entity="team",
    )


def test_serde_round_trip(wandb_run_config):
    assert copy_pydantic_json(wandb_run_config) == wandb_run_config


def test_wandb_path(wandb_run_config):
    assert wandb_run_config.wandb_path() == "team/research/run-id"


def test_ensure_run_id():
    env = WandbRunConfig(project="defined", entity="defined")
    assert env.id is not None  # Pydantic validator fills this in


def test_env_vars(wandb_run_config):
    env_vars = wandb_run_config.env_vars()
    expected = ["WANDB_PROJECT", "WANDB_ENTITY", "WANDB_RUN_ID"]
    for key in expected:
        assert key in env_vars
    assert "WANDB_RUN_GROUP" not in env_vars


def test_disallowed_kwargs():
    with pytest.raises(ValidationError):
        WandbRunConfig(project="project", old_name="I will throw")


def test_missing_key_warning(mock_environment_without_keys):
    with pytest.warns(UserWarning):
        config = WandbRunConfig(id="I am missing an API key", project="I should warn the user")
        assert "WANDB_API_KEY" not in config.env_vars()
