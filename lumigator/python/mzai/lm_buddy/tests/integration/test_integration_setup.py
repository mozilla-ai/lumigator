import os

import ray


def test_integration_env_vars():
    assert "RAY_STORAGE" in os.environ
    assert "WANDB_API_KEY" in os.environ
    assert "OPENAI_API_KEY" in os.environ

    wandb_mode = os.environ.get("WANDB_MODE")
    assert wandb_mode == "disabled"


def test_ray_runtime_env():
    ctx = ray.get_runtime_context()
    env_vars = ctx.runtime_env.env_vars()
    assert env_vars["WANDB_MODE"] == "disabled"
