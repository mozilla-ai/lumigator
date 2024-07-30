from enum import Enum


class Tags(str, Enum):
    HEALTH = "health"
    DATASETS = "datasets"
    FINETUNING = "finetuning"
    EXPERIMENTS = "experiments"
    EVENTS = "events"
    GROUNDTRUTH = "groundtruth"
    COMPLETIONS = "completions"


TAGS_METADATA = [
    {
        "name": Tags.HEALTH,
        "description": "Health check for the application.",
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
    },
    {
        "name": Tags.COMPLETIONS,
        "description": "Access models via external vendor endpoints",
    },
]
"""Metadata to associate with route tags in the OpenAPI documentation.

Reference: https://fastapi.tiangolo.com/tutorial/metadata/#metadata-for-tags
"""
