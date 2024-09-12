import click

from lm_buddy import LMBuddy
from lm_buddy.cli.utils import parse_config_option
from lm_buddy.configs.jobs import FinetuningJobConfig


@click.command(name="finetune", help="Run an LM Buddy finetuning job.")
@click.option("--config", type=str)
def command(config: str) -> None:
    config = parse_config_option(FinetuningJobConfig, config)
    buddy = LMBuddy()
    buddy.finetune(config)
