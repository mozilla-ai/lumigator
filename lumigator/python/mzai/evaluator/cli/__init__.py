import click

from evaluator.cli import evaluate


@click.group(name="Evaluator CLI", help="Entrypoints for the evaluator CLI ")
def cli():
    pass


cli.add_command(evaluate.group)
