from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import pandas as pd
import wandb


class JobType(str, Enum):
    """Enumeration of logical job types runnable via the LM Buddy."""

    PREPROCESSING = "preprocessing"
    FINETUNING = "finetuning"
    EVALUATION = "evaluation"


@dataclass
class JobResult:
    artifacts: list[wandb.Artifact]


@dataclass
class FinetuningResult(JobResult):
    """Result from a finetuning task."""

    checkpoint_path: Path | None
    metrics: dict[str, Any] | None
    is_adapter: bool


@dataclass
class EvaluationResult(JobResult):
    """Result from an evaluation task, containing aggregate metrics and artifacts."""

    tables: dict[str, pd.DataFrame]
    dataset_path: Path | None
