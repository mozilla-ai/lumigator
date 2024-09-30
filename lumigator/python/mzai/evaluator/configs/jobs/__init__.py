from configs.jobs.common import JobConfig

from configs.jobs.hf_evaluate import HuggingFaceEvalJobConfig
from configs.jobs.lm_harness import LMHarnessJobConfig


EvaluationJobConfig = LMHarnessJobConfig | HuggingFaceEvalJobConfig


__all__ = [
    "JobConfig",
    "LMHarnessJobConfig",
    "HuggingFaceEvalJobConfig",
    "EvaluationJobConfig",
]
