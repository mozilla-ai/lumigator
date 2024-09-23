from mzai.evaluator.configs.jobs.common import JobConfig

from mzai.evaluator.configs.jobs.hf_evaluate import HuggingFaceEvalJobConfig
from mzai.evaluator.configs.jobs.lm_harness import LMHarnessJobConfig

EvaluationJobConfig = (
    LMHarnessJobConfig | HuggingFaceEvalJobConfig
)

__all__ = [
    "JobConfig",
    "LMHarnessJobConfig",
    "HuggingFaceEvalJobConfig",
    "EvaluationJobConfig",
]
