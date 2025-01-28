"""Main entrypoint to the Evaluator CLI.

Makes the Evaluator CLI executable via `python -m evaluator`.
"""

from pathlib import Path
from typing import TypeVar

import click

from evaluator import entrypoint
from evaluator.configs.jobs import (
    HuggingFaceEvalJobConfig,
    LMHarnessJobConfig,
)
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
    evaluator = entrypoint.Evaluator()
    evaluator.evaluate(config)


@group.command("huggingface", help="Run the HuggingFace evaluation job.")
@click.option("--config", type=str)
def huggingface_command(config: str) -> None:
    print("starting HF eval...")
    config = parse_config_option(HuggingFaceEvalJobConfig, config)
    evaluator = entrypoint.Evaluator()
    evaluator.evaluate(config)


if __name__ == "__main__":
    cli()
