import json

import click

from mzai.jobrunner.runner import JobRunner


@click.command(name="Job Runner Entrypoint")
@click.argument("config", type=str)
def main(config: str):
    config = json.loads(config)
    runner = JobRunner()
    runner.run(config)


if __name__ == "__main__":
    main()
