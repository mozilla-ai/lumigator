import asyncio

import loguru
from fastapi import BackgroundTasks
from lumigator_schemas.experiments import ExperimentCreate, ExperimentResponse
from lumigator_schemas.jobs import (
    JobEvalCreate,
)

from backend.services.jobs import JobService


class ExperimentService:
    def __init__(self, job_service: JobService):
        self._job_service = job_service

    async def experiment_specific_background_task(self, job_id: str):
        job_status = "PENDING"
        loguru.logger.info(f"Job id: {job_id}")
        while job_status != "SUCCEEDED" and job_status != "FAILED":
            job_status = self._job_service.ray_client.get_job_status(job_id)
            loguru.logger.info(f"Job id: {job_id}, status: {job_status}")
            await asyncio.sleep(5)
        loguru.logger.info("The job completed")

    def create_experiment(
        self, request: ExperimentCreate, background_tasks: BackgroundTasks
    ) -> ExperimentResponse:
        # input is ExperimentCreate, we need to split the configs and generate one
        # JobInferenceCreate and one JobEvalCreate

        # submit inference job first
        job_response = self._job_service.create_job(
            JobEvalCreate.model_validate(request.model_dump()), background_tasks
        )

        # add a background task to wait until the previous job is completed
        background_tasks.add_task(self.experiment_specific_background_task, job_response.id)

        # append another task to submit another job afterwards
        # (NOTE: tasks in starlette are executed in order: https://www.starlette.io/background/)
        background_tasks.add_task(
            self._job_service.create_job,
            JobEvalCreate.model_validate(request.model_dump()),
            background_tasks,
        )

        return job_response
