from ray.job_submission import JobSubmissionClient

from src.settings import settings


def get_ray_job_client() -> JobSubmissionClient:
    return JobSubmissionClient(
        f"http://{settings.RAY_HEAD_NODE_HOST}:{settings.RAY_DASHBOARD_PORT}"
    )
