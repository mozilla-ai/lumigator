import wandb

from evaluator.configs.jobs import (
    EvaluationJobConfig,
    HuggingFaceEvalJobConfig,
    JobConfig,
    LMHarnessJobConfig,
)
from evaluator.jobs.common import (
    EvaluationResult,
    JobType,
)
from evaluator.jobs.evaluation.hf_evaluate import run_hf_evaluation
from evaluator.jobs.evaluation.lm_harness import run_lm_harness
from evaluator.paths import strip_path_prefix
from evaluator.tracking.run_utils import WandbResumeMode
from loguru import logger

import click

from evaluator.configs.jobs import (
    HuggingFaceEvalJobConfig,
    LMHarnessJobConfig,
)
from pathlib import Path
from typing import TypeVar

from evaluator.configs.jobs.common import JobConfig

ConfigType = TypeVar("ConfigType", bound=JobConfig)


def parse_config_option(config_cls: type[ConfigType], config: str) -> ConfigType:
    """Parse the config option string from the CLI.

    If it corresponds to a path that exists, attempt to load the config from YAML file.
    If not, attempt to parse it as a JSON string.
    """
    if Path(config).exists():
        return config_cls.from_yaml_file(config)
    else:
        return config_cls.model_validate_json(config)

@click.group(name="Evaluator CLI", help="Entrypoints for the evaluator CLI ")
def cli():
    pass


@click.group(name="evaluate", help="Run an evaluation job.")
def group() -> None:
    pass

cli.add_command(group)

@group.command("lm-harness", help="Run the lm-harness evaluation job.")
@click.option("--config", type=str)
def lm_harness_command(config: str) -> None:
    config = parse_config_option(LMHarnessJobConfig, config)
    evaluator = Evaluator()
    evaluator.evaluate(config)


@group.command("huggingface", help="Run the HuggingFace evaluation job.")
@click.option("--config", type=str)
def huggingface_command(config: str) -> None:
    print("starting HF eval...")
    config = parse_config_option(HuggingFaceEvalJobConfig, config)
    evaluator = Evaluator()
    evaluator.evaluate(config)


class Evaluator:
    """Simple wrapper around executable functions for tasks available in the library."""

    # TODO: Store some configuration (e.g., tracking info, name) globally
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
        print("evaluating...")
        logger.info("evaluating config: %s", config)
        match config:
            case LMHarnessJobConfig() as lm_harness_config:
                result = run_lm_harness(lm_harness_config)
            case HuggingFaceEvalJobConfig() as hf_eval_config:
                result = run_hf_evaluation(hf_eval_config)
            case _:
                raise ValueError(f"Invalid configuration for evaluation: {type(config)}")
        self._generate_artifact_lineage(config, result.artifacts, JobType.EVALUATION)
        return result
