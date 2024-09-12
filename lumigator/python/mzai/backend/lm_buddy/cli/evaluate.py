import click

from lm_buddy import LMBuddy
from lm_buddy.cli.utils import parse_config_option
from lm_buddy.configs.jobs import (
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
    buddy = LMBuddy()
    buddy.evaluate(config)


@group.command("prometheus", help="Run the prometheus evaluation job.")
@click.option("--config", type=str)
def prometheus_command(config: str) -> None:
    config = parse_config_option(PrometheusJobConfig, config)
    buddy = LMBuddy()
    buddy.evaluate(config)


@group.command("ragas", help="Run the ragas evaluation job.")
@click.option("--config", type=str)
def ragas_command(config: str) -> None:
    config = parse_config_option(RagasJobConfig, config)
    buddy = LMBuddy()
    buddy.evaluate(config)


@group.command("huggingface", help="Run the HuggingFace evaluation job.")
@click.option("--config", type=str)
def huggingface_command(config: str) -> None:
    config = parse_config_option(HuggingFaceEvalJobConfig, config)
    buddy = LMBuddy()
    buddy.evaluate(config)
