import click

from mzai.evaluator import Evaluator
from cli.utils import parse_config_option
from configs.jobs import (
    HuggingFaceEvalJobConfig,
    LMHarnessJobConfig,
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


@group.command("huggingface", help="Run the HuggingFace evaluation job.")
@click.option("--config", type=str)
def huggingface_command(config: str) -> None:
    config = parse_config_option(HuggingFaceEvalJobConfig, config)
    evaluate = Evaluator()
    evaluate.evaluate(config)
