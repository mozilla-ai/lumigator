"""Main entrypoint to the Evaluator CLI.

Makes the Evaluator CLI executable via `python -m evaluator`.
"""

from pathlib import Path
from typing import TypeVar
import click


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

@click.group(name="Inference CLI", help="Entrypoints for the Inference CLI ")
def cli():
    pass


@click.group(name="inference", help="Run an evaluation job.")
def group() -> None:
    pass

cli.add_command(group)

@cli.command("inference", help="Run the inference job.")
@click.option("--config", type=str)
def inference_command(config: str) -> None:
    print("starting inference...")
    config = parse_config_option(InferenceJobConfig, config)
    evaluator = inference.infer()
    evaluator.evaluate(config)

if __name__ == "__main__":
    cli()




