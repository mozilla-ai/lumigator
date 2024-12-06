import pytest
from backend.ray_submit.submission import RayJobEntrypoint


def test_parse_config(create_job_config):
    entrypoint_conf = RayJobEntrypoint(config=create_job_config)
    assert entrypoint_conf.config.dict() == create_job_config.dict()
