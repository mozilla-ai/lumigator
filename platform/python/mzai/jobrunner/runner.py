import random

from mzai.jobrunner.events import EventsClient
from mzai.schemas.jobs import JobConfig, JobStatus


class JobRunner:
    """Generic runner for platform jobs.

    Accepts a `JobConfig` which defines the type of job to run and its parameters,
    and dispatches to the appropriate implementation internally.
    """

    def __init__(self, events_client: EventsClient):
        self.events_client = events_client

    def on_begin(self, config: JobConfig) -> None:
        self.events_client.send(
            config.job_id,
            config.job_type,
            JobStatus.RUNNING,
            detail="Job started.",
        )

    def on_success(self, config: JobConfig) -> None:
        self.events_client.send(
            config.job_id,
            config.job_type,
            JobStatus.SUCCEEDED,
            detail="Job finished.",
        )

    def on_failure(self, config: JobConfig, exception: Exception) -> None:
        self.events_client.send(
            config.job_id,
            config.job_type,
            JobStatus.FAILED,
            detail=f"Job failed with exception: {exception}.",
        )

    def run(self, config: JobConfig):
        try:
            self.on_begin(config)
            if random.random() >= 0.5:
                raise ValueError("Job went crazy!")
            self.on_success(config)
        except Exception as e:
            self.on_failure(config, e)
