import json
from abc import ABC
from dataclasses import dataclass
from typing import Any

from ray.job_submission import JobSubmissionClient

from mzai.schemas.jobs import JobConfig


@dataclass(kw_only=True)
class RayJobEntrypoint(ABC):
    """A generic command which is passed a config and submitted as a ray job.

    Currently the only command we run is `lm-buddy evaluate`, but this can
    be parametrised to support both different parameters (e.g. `lm-buddy
    evaluate lm-harness`, `lm-buddy finetune`, etc) or even different commands.
    """

    config: JobConfig
    runtime_env: dict[str, Any] | None = None
    num_cpus: int | float | None = None
    num_gpus: int | float | None = None
    memory: int | float | None = None

    @property
    def command(self) -> str:
        # lm-buddy passed as a module to Ray using a JSON-serialized config.
        return (f"python -m lumigator.python.mzai.backend.lm_buddy evaluate huggingface "
                f"--config '{json.dumps(self.config.args)}'")


def submit_ray_job(client: JobSubmissionClient, entrypoint: RayJobEntrypoint) -> str:
    return client.submit_job(
        entrypoint=entrypoint.command,
        entrypoint_num_cpus=entrypoint.num_cpus,
        entrypoint_num_gpus=entrypoint.num_gpus,
        entrypoint_memory=entrypoint.memory,
        runtime_env=entrypoint.runtime_env,
        submission_id=str(
            entrypoint.config.job_id
        ),  # Use the record ID for the Ray submission
    )
