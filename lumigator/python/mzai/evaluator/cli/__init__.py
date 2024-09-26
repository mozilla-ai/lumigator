import click

from mzai.evaluator.cli import evaluate


@click.group(name="Evaluator CLI", help="Entrypoints for the evaluator.")
def cli():
    pass


cli.add_command(evaluate.group)
