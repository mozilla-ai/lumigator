import os
from pathlib import Path

EVALUATOR_HOME_PATH: str = os.getenv(
    "EVALUATOR_HOME",
    str(Path.home() / ".evaluator"),
)

EVALUATOR_RESULTS_PATH: str = os.getenv(
    "EVALUATOR_RESULTS",
    f"{EVALUATOR_HOME_PATH}/results",
)
