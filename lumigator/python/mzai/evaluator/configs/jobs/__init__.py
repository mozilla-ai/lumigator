from mzai.evaluator.configs.jobs.common import JobConfig

from mzai.evaluator.configs.jobs.hf_evaluate import HuggingFaceEvalJobConfig
from mzai.evaluator.configs.jobs.lm_harness import LMHarnessJobConfig
from mzai.evaluator.configs.jobs.prometheus import PrometheusJobConfig
from mzai.evaluator.configs.jobs.ragas import RagasJobConfig

EvaluationJobConfig = (
    LMHarnessJobConfig | PrometheusJobConfig | RagasJobConfig | HuggingFaceEvalJobConfig
)

__all__ = [
    "JobConfig",
    "LMHarnessJobConfig",
    "PrometheusJobConfig",
    "RagasJobConfig",
    "HuggingFaceEvalJobConfig",
    "EvaluationJobConfig",
]
