import time
from contextlib import contextmanager
from uuid import UUID

from loguru import logger
from ray.job_submission import JobDetails, JobSubmissionClient

from mzai.backend.db import session_manager
from mzai.backend.repositories.finetuning import FinetuningJobRepository
from mzai.backend.settings import settings
from mzai.schemas.jobs import JobStatus


class FinetuningJobHandler:
    """Handler for monitoring/updating the results of a finetuning job.

    Currently implemented by polling the Ray jobs API for terminal status.
    """

    def __init__(self, job_id: UUID, submission_id: str):
        self.job_id = job_id
        self.submission_id = submission_id
        self.ray_client = JobSubmissionClient(settings.RAY_DASHBOARD_URL)

    @contextmanager
    def _get_finetuning_service(self):
        from mzai.backend.services.finetuning import FinetuningService

        # We should avoid injecting API dependencies into the handlers that run in the background
        # This is to avoid DB sessions from the API hanging while the background task runs
        # Discussion: https://github.com/tiangolo/fastapi/discussions/8502
        with session_manager.session() as session:
            job_repo = FinetuningJobRepository(session)
            yield FinetuningService(job_repo, self.ray_client)

    def _on_complete(self, details: JobDetails) -> None:
        # TODO: Also create a record in the Models table here
        logger.info(f"Finetuning job {self.job_id} finished with details {details}")
        with self._get_finetuning_service() as finetuning_service:
            status = JobStatus.from_ray(details.status)
            finetuning_service.update_job_status(self.job_id, status)

    def poll(
        self,
        *,
        interval: float = 5.0,
        timeout: float | None = None,
    ) -> None:
        start_time = time.time()
        timeout = timeout or float("inf")

        while True:
            details = self.ray_client.get_job_info(self.submission_id)
            logger.info(f"Polling for finetuning job {self.job_id}', status = {details.status}")
            if details.status.is_terminal():
                self._on_complete(details)
                break

            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                msg = f"Polling for finetuning job {self.job_id} failed due to timeout."
                logger.error(msg)
                raise TimeoutError(msg)

            time.sleep(interval)
