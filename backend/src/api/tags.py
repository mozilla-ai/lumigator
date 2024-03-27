from enum import Enum


class Tags(str, Enum):
    HEALTH = "health"
    FINETUNING = "finetuning"


tags_metadata = [
    {
        "name": Tags.HEALTH,
        "description": "Health check for the application.",
    },
    {
        "name": Tags.FINETUNING,
        "description": "Create and manage finetuning jobs.",
    },
]
