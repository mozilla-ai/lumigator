import click
from loguru import logger

from mzai.jobrunner.runner import JobRunner
from mzai.schemas.jobs import JobConfig


@click.command(name="Job Runner Entrypoint")
@click.option("--config", type=str)
def main(config: str):
    logger.info(f"Job runner called with config = {config}")
    config = JobConfig.model_validate_json(config)
    runner = JobRunner()
    runner.run(config)


if __name__ == "__main__":
    main()
