from typing import Annotated

from fastapi import Depends
from ray.job_submission import JobSubmissionClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.utils.ray import get_ray_client

DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
RayClientDep = Annotated[JobSubmissionClient, Depends(get_ray_client)]
