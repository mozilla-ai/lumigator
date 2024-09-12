import click

from lm_buddy.cli import evaluate, finetune


@click.group(name="LM Buddy CLI", help="Entrypoints for the LM Buddy.")
def cli():
    pass


cli.add_command(finetune.command)
cli.add_command(evaluate.group)
