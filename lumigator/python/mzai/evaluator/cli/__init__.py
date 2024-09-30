import click

from cli import evaluate


@click.group(name="Evaluator CLI", help="Entrypoints for the ")
def cli():
    pass


cli.add_command(evaluate.group)
