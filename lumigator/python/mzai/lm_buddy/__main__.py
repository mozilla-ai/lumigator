"""Main entrypoint to the LM Buddy CLI.

Makes the LM Buddy CLI executable via `python -m lm_buddy`.
"""

from lumigator.python.mzai.lm_buddy.cli import cli

if __name__ == "__main__":
    cli()
