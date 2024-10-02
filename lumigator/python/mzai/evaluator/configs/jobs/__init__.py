from evaluator.configs.jobs.common import JobConfig

from evaluator.configs.jobs.hf_evaluate import HuggingFaceEvalJobConfig
from evaluator.configs.jobs.lm_harness import LMHarnessJobConfig


EvaluationJobConfig = LMHarnessJobConfig | HuggingFaceEvalJobConfig


__all__ = [
    "JobConfig",
    "LMHarnessJobConfig",
    "HuggingFaceEvalJobConfig",
    "EvaluationJobConfig",
]
