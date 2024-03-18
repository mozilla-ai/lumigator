from collections.abc import Generator

from ray.job_submission import JobSubmissionClient

from app.core.settings import settings


def get_ray_client() -> Generator[JobSubmissionClient, None, None]:
    address = f"http://{settings.RAY_HEAD_NODE_IP}:{settings.RAY_HEAD_NODE_PORT}"
    yield JobSubmissionClient(address)
