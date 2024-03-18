from collections.abc import AsyncGenerator, Generator
from typing import Annotated

from app.config import settings
from app.db import session_manager
from fastapi import Depends
from ray.job_submission import JobSubmissionClient
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session() -> AsyncGenerator[AsyncSession, None, None]:
    async with session_manager.session() as session:
        yield session


def get_ray_client() -> Generator[JobSubmissionClient, None, None]:
    address = f"http://{settings.RAY_HEAD_NODE_IP}:{settings.RAY_HEAD_NODE_PORT}"
    yield JobSubmissionClient(address)


DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
RayClientDep = Annotated[JobSubmissionClient, Depends(get_ray_client)]
