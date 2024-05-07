from contextlib import contextmanager
from uuid import UUID

import requests
from loguru import logger
from requests.adapters import HTTPAdapter, Retry

from mzai.schemas.jobs import JobEvent, JobStatus, JobType

DEFAULT_STATUS_FORCELIST = [429, 500, 502, 503, 504]


class EventsClient:
    def __init__(
        self,
        events_url: str,
        max_retries: int = 5,
        backoff_factor: float = 0.1,
        status_forcelist: list[int] = DEFAULT_STATUS_FORCELIST,
    ):
        self.events_url = events_url
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist

    @contextmanager
    def _get_session(self):
        """Initialize a requests session with a retry adapter included.

        The session object includes auto-retry capabilities for all http/https requests.
        After exiting this context manager, the session is closed.
        """
        with requests.Session() as session:
            retries = Retry(
                total=self.max_retries,
                backoff_factor=self.backoff_factor,
                status_forcelist=self.status_forcelist,  # HTTP status codes to retry on
            )
            # Binds the adapter to any endpoint prefixed with 'http://' or 'https://'
            session.mount("http://", HTTPAdapter(max_retries=retries))
            session.mount("https://", HTTPAdapter(max_retries=retries))
            yield session

    def send(
        self,
        job_id: UUID,
        job_type: JobType,
        status: JobStatus,
        detail: str | None = None,
    ) -> None:
        event = JobEvent(job_id=job_id, job_type=job_type, status=status, detail=detail)
        event_json = event.model_dump(mode="json")
        logger.info(f"Sending job event {event_json}")
        with self._get_session() as session:
            response = session.post(url=self.events_url, json=event_json)
            if response.status_code != 200:
                logger.error(f"Failed to send event for job '{job_id}': {response.json()}")
