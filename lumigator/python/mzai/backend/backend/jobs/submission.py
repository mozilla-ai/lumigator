from abc import ABC
from dataclasses import dataclass
from typing import Any

import loguru
from ray.job_submission import JobSubmissionClient
from schemas.jobs import JobConfig


@dataclass(kw_only=True)
class RayJobEntrypoint(ABC):
    """A generic command which is passed a config and submitted as a ray job.

    Currently the command is passed as a parameter. It likely will be a ptyhon module used via cli
    (e.g. `lm-buddy evaluate lm-harness`, `lm-buddy finetune`, etc) or even different commands.
    Note parameters of this command can either be passed in a config file, or left empty.
    """

    config: JobConfig
    runtime_env: dict[str, Any] | None = None
    num_cpus: int | float | None = None
    num_gpus: int | float | None = None
    memory: int | float | None = None

    @property
    def command(self) -> str:
        full_command = self.config.command

        if self.config.args:
            for k in self.config.args.keys():
                full_command += f" {k} '{self.config.args[k]}'"

        return full_command


def submit_ray_job(client: JobSubmissionClient, entrypoint: RayJobEntrypoint) -> str:
    loguru.logger.info(f"Submitting {entrypoint.command}...{entrypoint.runtime_env}")
    return client.submit_job(
        entrypoint=entrypoint.command,
        entrypoint_num_cpus=entrypoint.num_cpus,
        entrypoint_num_gpus=entrypoint.num_gpus,
        entrypoint_memory=entrypoint.memory,
        runtime_env=entrypoint.runtime_env,
        submission_id=str(entrypoint.config.job_id),  # Use the record ID for the Ray submission
    )
