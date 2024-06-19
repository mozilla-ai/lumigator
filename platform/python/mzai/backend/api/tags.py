from enum import Enum


class Tags(str, Enum):
    HEALTH = "health"
    DATASETS = "datasets"
    FINETUNING = "finetuning"
    EXPERIMENTS = "experiments"
    EVENTS = "events"
    TEST = "TEST"
    GROUNDTRUTH = "GROUNDTRUTH"


TAGS_METADATA = [
    {
        "name": Tags.HEALTH,
        "description": "Health check for my app.",
    },
    {
        "name": Tags.DATASETS,
        "description": "Upload and download datasets.",
    },
    {
        "name": Tags.FINETUNING,
        "description": "Create and manage finetuning jobs.",
    },
    {
        "name": Tags.EXPERIMENTS,
        "description": "Create and manage evaluation experiments.",
    },
    {
        "name": Tags.EVENTS,
        "description": "Send a job event to the application.",
    },
    {
        "name": Tags.GROUNDTRUTH,
        "description": "Create and manage ground truth generation",
    }
]
"""Metadata to associate with route tags in the OpenAPI documentation.

Reference: https://fastapi.tiangolo.com/tutorial/metadata/#metadata-for-tags
"""
