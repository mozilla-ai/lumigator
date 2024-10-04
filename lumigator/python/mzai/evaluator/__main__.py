"""Main entrypoint to the Evaluator CLI.
"""

from evaluator.cli.utils import parse_config_option
from evaluator.configs.jobs import (
    HuggingFaceEvalJobConfig,
    LMHarnessJobConfig,
)
from evaluator.entrypoint import Evaluator


def lm_harness_command(config: str) -> None:
    config = parse_config_option(LMHarnessJobConfig, config)
    evaluator = Evaluator()
    evaluator.evaluate(config)


def huggingface_command(config: str) -> None:
    print("starting HF eval...")
    config = parse_config_option(HuggingFaceEvalJobConfig, config)
    evaluator = Evaluator()
    evaluator.evaluate(config)

