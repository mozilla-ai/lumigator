import random

from mzai.jobrunner.events import send_job_event
from mzai.schemas.jobs import JobConfig, JobStatus


class JobRunner:
    """Generic runner for platform jobs.

    Accepts a `JobConfig` which defines the type of job to run and its parameters,
    and dispatches to the appropriate implementation internally.
    """

    def __init__(self):
        pass

    def on_begin(self, config: JobConfig) -> None:
        send_job_event(config.job_id, config.job_type, JobStatus.RUNNING, detail="Job started.")

    def on_success(self, config: JobConfig) -> None:
        send_job_event(config.job_id, config.job_type, JobStatus.SUCCEEDED, detail="Job finished.")

    def on_failure(self, config: JobConfig, exception: Exception) -> None:
        send_job_event(
            config.job_id,
            config.job_type,
            JobStatus.FAILED,
            detail=f"Job failed with exception: {exception}.",
        )

    def run(self, config: JobConfig):
        self.on_begin(config)
        try:
            if random.random() >= 0.5:
                raise ValueError("Job went crazy!")
            self.on_success(config)
        except Exception as e:
            self.on_failure(config, e)
