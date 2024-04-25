from mzai.schemas.jobs import JobEvent, JobStatus


def send_event(status: JobStatus, detail: str | None = None):
    event = JobEvent(status=status, detail=detail)
