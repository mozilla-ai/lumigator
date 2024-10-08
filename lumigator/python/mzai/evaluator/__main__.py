"""Main entrypoint to the Evaluator CLI.

Makes the Evaluator CLI executable via `python -m evaluator`.
"""

from evaluator import entrypoint

if __name__ == "__main__":
    entrypoint.cli()
