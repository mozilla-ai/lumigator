from enum import Enum


class Tags(str, Enum):
    HEALTH = "health"
    FINETUNING = "finetuning"


TAGS_METADATA = [
    {
        "name": Tags.HEALTH,
        "description": "Health check for the application.",
    },
    {
        "name": Tags.FINETUNING,
        "description": "Create and manage finetuning jobs.",
    },
]
"""Metadata to associate with route tags in the OpenAPI documentation.

Reference: https://fastapi.tiangolo.com/tutorial/metadata/#metadata-for-tags
"""
