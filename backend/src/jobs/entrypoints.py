from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from ray.job_submission import JobSubmissionClient


@dataclass(kw_only=True)
class RayJobEntrypoint(ABC):
    runtime_env: dict[str, Any] | None = None
    num_cpus: int | float | None = None
    num_gpus: int | float | None = None
    memory: int | float | None = None

    @property
    @abstractmethod
    def command(self) -> str:
        pass


@dataclass(kw_only=True)
class FinetuningJobEntrypoint(RayJobEntrypoint):
    config: dict[str, Any]

    @property
    def command(self) -> str:
        # TODO: Dummy entrypoint logic that needs to be updated for real
        return "echo 'Hello from Ray!'"


def submit_ray_job(client: JobSubmissionClient, entrypoint: RayJobEntrypoint) -> str:
    return client.submit_job(
        entrypoint=entrypoint.command,
        entrypoint_num_cpus=entrypoint.num_cpus,
        entrypoint_num_gpus=entrypoint.num_gpus,
        entrypoint_memory=entrypoint.memory,
        runtime_env=entrypoint.runtime_env,
    )
