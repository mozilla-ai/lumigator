import click

from mzai.evaluator import Evaluator
from mzai.evaluator.cli.utils import parse_config_option
from mzai.evaluator.configs.jobs import (
    HuggingFaceEvalJobConfig,
    LMHarnessJobConfig,
    PrometheusJobConfig,
    RagasJobConfig,
)


@click.group(name="evaluate", help="Run an LM Buddy evaluation job.")
def group() -> None:
    pass


@group.command("lm-harness", help="Run the lm-harness evaluation job.")
@click.option("--config", type=str)
def lm_harness_command(config: str) -> None:
    config = parse_config_option(LMHarnessJobConfig, config)
    evaluate = Evaluator()
    evaluate.evaluate(config)


@group.command("prometheus", help="Run the prometheus evaluation job.")
@click.option("--config", type=str)
def prometheus_command(config: str) -> None:
    config = parse_config_option(PrometheusJobConfig, config)
    evaluate = Evaluator()
    evaluate.evaluate(config)


@group.command("ragas", help="Run the ragas evaluation job.")
@click.option("--config", type=str)
def ragas_command(config: str) -> None:
    config = parse_config_option(RagasJobConfig, config)
    evaluate = Evaluator()
    evaluate.evaluate(config)


@group.command("huggingface", help="Run the HuggingFace evaluation job.")
@click.option("--config", type=str)
def huggingface_command(config: str) -> None:
    config = parse_config_option(HuggingFaceEvalJobConfig, config)
    evaluate = Evaluator()
    evaluate.evaluate(config)
