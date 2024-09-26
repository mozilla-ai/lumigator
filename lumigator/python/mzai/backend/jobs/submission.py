import json
from abc import ABC
from dataclasses import dataclass
from typing import Any

from ray.job_submission import JobSubmissionClient

from mzai.schemas.jobs import JobConfig


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
        # The reasoning is: if the user wants to dump a full command with some flags (not necessarily ray configs
        # or some such), they dump it on raw_command. If they do want to provide configuration, they can make use
        # of `config_keyword` (to keep this naming flexible) and `config.args` to pass the fields on.
        full_command = self.raw_command

        if self.config.args != "":
            # TODO: This is a hack to get around the fact that the args are passed as a string.
            full_command += f" --{self.config_keyword} '{json.dumps(self.config.args)}'"

        return full_command


def submit_ray_job(client: JobSubmissionClient, entrypoint: RayJobEntrypoint) -> str:
    return client.submit_job(
        entrypoint=entrypoint.command,
        entrypoint_num_cpus=entrypoint.num_cpus,
        entrypoint_num_gpus=entrypoint.num_gpus,
        entrypoint_memory=entrypoint.memory,
        runtime_env=entrypoint.runtime_env,
        submission_id=str(entrypoint.config.job_id),  # Use the record ID for the Ray submission
    )
