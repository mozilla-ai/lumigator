from enum import Enum


class Tags(str, Enum):
    HEALTH = "health"
    DATASETS = "datasets"
    EXPERIMENTS = "experiments"
    GROUNDTRUTH = "groundtruth"
    COMPLETIONS = "completions"
    TASKS = "tasks"


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
        "name": Tags.EXPERIMENTS,
        "description": "Create and manage evaluation experiments.",
    },
    {
        "name": Tags.GROUNDTRUTH,
        "description": "Create and manage ground truth generation",
    },
    {
        "name": Tags.COMPLETIONS,
        "description": "Access models via external vendor endpoints",
    },
    {
        "name": Tags.TASKS,
        "description": "Mapping model lists to tasks.",
    },
]
"""Metadata to associate with route tags in the OpenAPI documentation.

Reference: https://fastapi.tiangolo.com/tutorial/metadata/#metadata-for-tags
"""
