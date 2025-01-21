from abc import ABC
from dataclasses import dataclass
from typing import Any

import loguru
from lumigator_schemas.jobs import JobConfig
from ray.job_submission import JobSubmissionClient


@dataclass(kw_only=True)
class RayJobEntrypoint(ABC):
    config: JobConfig
    metadata: dict[str, Any] | None = None
    runtime_env: dict[str, Any] | None = None
    num_cpus: int | float | None = None
    num_gpus: int | float | None = None
    memory: int | float | None = None

    @property
    def get_command_with_params(self) -> str:
        """A generic command which is passed some optional args and submitted as a ray job.

        Note that parameters can either be passed as config.args (a dictionary containing
        parameter names as keys and parameter values as values) or directly with the command
        string.
        """
        full_command = self.config.command

        if self.config.args:
            for k in self.config.args.keys():
                full_command += f" {k} '{self.config.args[k]}'"

        return full_command


def submit_ray_job(client: JobSubmissionClient, entrypoint: RayJobEntrypoint) -> str:
    loguru.logger.info(
        f"Submitting {entrypoint.get_command_with_params}...{entrypoint.runtime_env}"
    )

    return client.submit_job(
        entrypoint=entrypoint.get_command_with_params,
        metadata=entrypoint.metadata,
        entrypoint_num_cpus=entrypoint.num_cpus,
        entrypoint_num_gpus=entrypoint.num_gpus,
        entrypoint_memory=entrypoint.memory,
        runtime_env=entrypoint.runtime_env,
        submission_id=str(entrypoint.config.job_id),  # Use the record ID for the Ray submission
    )
