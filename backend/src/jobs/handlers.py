import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from uuid import UUID

from loguru import logger
from ray.job_submission import JobDetails

from src.db import session_manager
from src.repositories.finetuning import FinetuningJobRepository
from src.schemas.extras import JobStatus
from src.utils import get_ray_job_client


class RayJobHandler(ABC):
    """Interface for polling Ray jobs for completion and handling the results."""

    def __init__(self, submission_id: str):
        self.submission_id = submission_id
        self.ray_client = get_ray_job_client()

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
            logger.info(f"Polling for Ray job '{self.submission_id}', status = {details.status}")
            if details.status.is_terminal():
                self.on_complete(details)
                break

            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                msg = f"Polling for job {self} failed due to timeout."
                logger.error(msg)
                raise TimeoutError(msg)

            time.sleep(interval)

    @abstractmethod
    def on_complete(self, details: JobDetails) -> None:
        pass


class FinetuningJobHandler(RayJobHandler):
    def __init__(self, job_id: UUID, submission_id: str):
        super().__init__(submission_id)
        self.job_id = job_id

    @contextmanager
    def _get_finetuning_service(self):
        from src.services.finetuning import FinetuningService

        # We should avoid injecting API dependencies into the handlers that run in the background
        # This is to avoid DB sessions from the API hanging while the background task runs
        # Discussion: https://github.com/tiangolo/fastapi/discussions/8502
        with session_manager.session() as session:
            job_repo = FinetuningJobRepository(session)
            yield FinetuningService(job_repo, self.ray_client)

    def on_complete(self, details: JobDetails) -> None:
        # TODO: Also create a record in the Models table here
        logger.info(f"Finetuning job {self.job_id} finished with details {details}")
        with self._get_finetuning_service() as finetuning_service:
            status = JobStatus.from_ray(details.status)
            finetuning_service.update_job_status(self.job_id, status)
