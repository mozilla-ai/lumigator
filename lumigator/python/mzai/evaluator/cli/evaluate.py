import click

from evaluator.entrypoint import Evaluator
from evaluator.cli.utils import parse_config_option
from evaluator.configs.jobs import (
    HuggingFaceEvalJobConfig,
    LMHarnessJobConfig,
)


@click.group(name="evaluate", help="Run an evaluation job.")
def group() -> None:
    pass


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
