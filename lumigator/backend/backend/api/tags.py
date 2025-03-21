from enum import Enum


class Tags(str, Enum):
    HEALTH = "health"
    DATASETS = "datasets"
    JOBS = "jobs"
    EXPERIMENTS = "experiments"
    WORKFLOWS = "workflows"
    MODELS = "models"
    SETTINGS = "settings"


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
        "name": Tags.WORKFLOWS,
        "description": "Create and manage workflows.",
    },
    {
        "name": Tags.JOBS,
        "description": "Create and manage jobs running on Ray.",
    },
    {
        "name": Tags.MODELS,
        "description": "Return a list of suggested models for a given task.",
    },
    {
        "name": Tags.SETTINGS,
        "description": "Manage settings.",
    },
]
"""Metadata to associate with route tags in the OpenAPI documentation.

Reference: https://fastapi.tiangolo.com/tutorial/metadata/#metadata-for-tags
"""
