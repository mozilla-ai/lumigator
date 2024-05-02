from abc import ABC
from dataclasses import dataclass
from typing import Any

from ray.job_submission import JobSubmissionClient

from mzai.schemas.jobs import JobConfig


@dataclass(kw_only=True)
class RayJobEntrypoint(ABC):
    config: JobConfig
    runtime_env: dict[str, Any] | None = None
    num_cpus: int | float | None = None
    num_gpus: int | float | None = None
    memory: int | float | None = None

    @property
    def command(self) -> str:
        return f"./jobrunner.pex --config '{self.config.model_dump_json()}'"


def submit_ray_job(client: JobSubmissionClient, entrypoint: RayJobEntrypoint) -> str:
    return client.submit_job(
        entrypoint=entrypoint.command,
        entrypoint_num_cpus=entrypoint.num_cpus,
        entrypoint_num_gpus=entrypoint.num_gpus,
        entrypoint_memory=entrypoint.memory,
        runtime_env=entrypoint.runtime_env,
        submission_id=str(entrypoint.config.job_id),  # Use the record ID for the Ray submission
    )
