from mzai.evaluator.configs.jobs.common import JobConfig

from mzai.evaluator.configs.jobs.hf_evaluate import HuggingFaceEvalJobConfig
from mzai.evaluator.configs.jobs.lm_harness import LMHarnessJobConfig
from mzai.evaluator.configs.jobs.ragas import RagasJobConfig

EvaluationJobConfig = (
    LMHarnessJobConfig | RagasJobConfig | HuggingFaceEvalJobConfig
)

__all__ = [
    "JobConfig",
    "LMHarnessJobConfig",
    "RagasJobConfig",
    "HuggingFaceEvalJobConfig",
    "EvaluationJobConfig",
]
