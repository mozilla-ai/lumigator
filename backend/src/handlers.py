import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from uuid import UUID

from loguru import logger
from ray.job_submission import JobDetails

from src.api.deps import get_ray_client
from src.db import session_manager
from src.repositories.finetuning import FinetuningJobRepository
from src.schemas.extras import JobStatus
from src.services.finetuning import FinetuningService


class RayJobHandler(ABC):
    """Interface for polling Ray jobs for completion and handling the results."""

    def poll(
        self,
        submission_id: UUID,
        *,
        interval: float = 5.0,
        timeout: float | None = None,
    ) -> None:
        start_time = time.time()
        timeout = timeout or float("inf")

        ray_client = get_ray_client()
        while True:
            job_info = ray_client.get_job_info(submission_id)
            if job_info.status.is_terminal():
                self.on_complete(job_info)
                break

            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                msg = f"Polling for Ray job submission {submission_id} failed due to timeout."
                logger.error(msg)
                raise TimeoutError(msg)

            time.sleep(interval)

    @abstractmethod
    def on_complete(self, status: JobStatus) -> None:
        pass


class FinetuningJobHandler(RayJobHandler):
    def __init__(self, job_id: UUID):
        self.job_id = job_id

    @staticmethod
    @contextmanager
    def _get_finetuning_service():
        with session_manager.session() as session:
            job_repo = FinetuningJobRepository(session)
            ray_client = get_ray_client()
            yield FinetuningService(job_repo, ray_client)

    def on_complete(self, job_info: JobDetails) -> None:
        # TODO: Also create a record in the Models table here
        logger.info(f"Finetuning job {self.job_id} finished with details {job_info}")
        with self._get_finetuning_service() as service:
            status = JobStatus.from_ray(job_info.status)
            service.update_job_status(self.job_id, status)
