from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Job:
    type: str | None = None
    job_id: Optional[str] = None
    submission_id: str | None = None
    driver_info: Optional[str] = None
    status: str | None = None
    entrypoint: str | None = None
    message: str | None = None
    error_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: dict | None = None
    runtime_env: dict | None = None
    driver_agent_http_address: str | None = None
    driver_node_id: str | None = None
    driver_exit_code: int | None = None