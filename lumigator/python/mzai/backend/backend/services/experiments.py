import json
import time

import loguru
import requests
from fastapi import BackgroundTasks
from lumigator_schemas.experiments import ExperimentCreate, ExperimentResponse
from lumigator_schemas.jobs import (
    JobEvalCreate,
)

from backend.services.jobs import JobService


class ExperimentService:
    def __init__(self, job_service: JobService):
        self._job_service = job_service

    def experiment_specific_background_task(self, job_id: str):
        status = "PENDING"
        loguru.logger.info(f"Job id: {job_id}")
        while status != "SUCCEEDED" and status != "FAILED":
            res = requests.get(f"http://localhost:8000/api/v1/health/jobs/{job_id}")
            status = json.loads(res.text)["status"]
            loguru.logger.info(f"Job id: {job_id}, status: {status}")
            time.sleep(5)
        loguru.logger.info("The job completed")

    def create_experiment(
        self, request: ExperimentCreate, background_tasks: BackgroundTasks
    ) -> ExperimentResponse:
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
