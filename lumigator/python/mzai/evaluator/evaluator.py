import wandb

from mzai.evaluator.configs.jobs import (
    EvaluationJobConfig,
    HuggingFaceEvalJobConfig,
    JobConfig,
    LMHarnessJobConfig,
    PrometheusJobConfig,
    RagasJobConfig,
)
from mzai.evaluator.jobs.common import (
    EvaluationResult,
    FinetuningResult,
    JobType,
)
from mzai.evaluator.jobs.evaluation.hf_evaluate import run_hf_evaluation
from mzai.evaluator.jobs.evaluation.lm_harness import run_lm_harness
from mzai.evaluator.jobs.evaluation.ragas import run_ragas
from mzai.evaluator.paths import strip_path_prefix
from mzai.evaluator.tracking.run_utils import WandbResumeMode


class Evaluator:
    """Your buddy in the (L)LM space.

    Simple wrapper around executable functions for tasks available in the library.
    """

    # TODO: Store some configuration (e.g., tracking info, name) globally on the buddy
    def __init__(self):
        pass

    def _generate_artifact_lineage(
        self, config: JobConfig, results: list[wandb.Artifact], job_type: JobType
    ) -> None:
        """Link input artifacts and log output artifacts to a run.

        A no-op if no tracking config is available.
        """
        if config.tracking is not None:
            with wandb.init(
                name=config.name,
                job_type=job_type,
                resume=WandbResumeMode.ALLOW,
                **config.tracking.model_dump(),
            ) as run:
                for path in config.artifact_paths():
                    artifact_name = strip_path_prefix(path)
                    run.use_artifact(artifact_name)
                for artifact in results:
                    artifact = run.log_artifact(artifact)
                    artifact.wait()

    def evaluate(self, config: EvaluationJobConfig) -> EvaluationResult:
        """Run an evaluation job with the provided configuration.

        The underlying evaluation framework is determined by the configuration type.
        """
        match config:
            case LMHarnessJobConfig() as lm_harness_config:
                result = run_lm_harness(lm_harness_config)
            case PrometheusJobConfig() as prometheus_config:
                result = run_prometheus(prometheus_config)
            case RagasJobConfig() as ragas_config:
                result = run_ragas(ragas_config)
            case HuggingFaceEvalJobConfig() as hf_eval_config:
                result = run_hf_evaluation(hf_eval_config)
            case _:
                raise ValueError(f"Invlid configuration for evaluation: {type(config)}")
        self._generate_artifact_lineage(config, result.artifacts, JobType.EVALUATION)
        return result
