from enum import Enum
from typing import Any

import wandb
from wandb.apis.public import Run as ApiRun

from lm_buddy.configs.wandb import WandbRunConfig


class WandbResumeMode(str, Enum):
    """Enumeration of modes for resuming a W&B run.

    This is not an exahustive list of the values that can be passed to the W&B SDK
    (Docs: https://docs.wandb.ai/ref/python/init), but just those commonly used within the package.
    """

    ALLOW = "allow"
    MUST = "must"
    NEVER = "never"


def get_run_from_api(config: WandbRunConfig) -> ApiRun:
    """Retrieve a run from the W&B API."""
    api = wandb.Api()
    return api.run(config.wandb_path())


def get_run_summary(config: WandbRunConfig) -> dict[str, Any]:
    """Get the summary dictionary attached to a W&B run."""
    run = get_run_from_api(config)
    return dict(run.summary)


def update_wandb_summary(config: WandbRunConfig, metrics: dict[str, Any]) -> None:
    """Update a run's summary with the provided metrics."""
    run = get_run_from_api(config)
    run.summary.update(metrics)
    run.update()
