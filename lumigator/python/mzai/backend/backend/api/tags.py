from enum import Enum


class Tags(str, Enum):
    HEALTH = "health"
    DATASETS = "datasets"
    JOBS = "jobs"
    COMPLETIONS = "completions"
    EXPERIMENTS = "experiments"
    RUNS = "runs"
    MODELS = "models"


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
        "description": "Create and manage experiments.",
    },
    {
        "name": Tags.RUNS,
        "description": "Create and manage runs (NOT YET AVAILABLE).",
    },
    {
        "name": Tags.JOBS,
        "description": "Create and manage jobs running on Ray.",
    },
    {
        "name": Tags.COMPLETIONS,
        "description": "Access models via external vendor endpoints",
    },
    {
        "name": Tags.MODELS,
        "description": "Return a list of suggested models for a given task.",
    },
]
"""Metadata to associate with route tags in the OpenAPI documentation.

Reference: https://fastapi.tiangolo.com/tutorial/metadata/#metadata-for-tags
"""
