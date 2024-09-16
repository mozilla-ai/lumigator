import os
from pathlib import Path

LM_BUDDY_HOME_PATH: str = os.getenv(
    "LM_BUDDY_HOME",
    str(Path.home() / ".lm_buddy"),
)

LM_BUDDY_RESULTS_PATH: str = os.getenv(
    "LM_BUDDY_RESULTS",
    f"{LM_BUDDY_HOME_PATH}/results",
)
