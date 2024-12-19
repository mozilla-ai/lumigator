import asyncio
from uuid import UUID

import loguru
from fastapi import BackgroundTasks
from lumigator_schemas.experiments import ExperimentCreate, ExperimentResponse
from lumigator_schemas.jobs import (
    JobEvalCreate,
    JobInferenceCreate,
)

from backend.services.datasets import DatasetService
from backend.services.jobs import JobService


class ExperimentService:
    def __init__(self, job_service: JobService, dataset_service: DatasetService):
        self._job_service = job_service
        self._dataset_service = dataset_service

    async def experiment_specific_background_task(self, job_id: str):
        job_status = "PENDING"
        loguru.logger.info(f"Job id: {job_id}")
        while job_status != "SUCCEEDED" and job_status != "FAILED":
            job_status = self._job_service.ray_client.get_job_status(job_id)
            loguru.logger.info(f"Job id: {job_id}, status: {job_status}")
            await asyncio.sleep(5)
        loguru.logger.info("The job completed")

    def _run_eval(
        self, inference_job_id: UUID, request: ExperimentCreate, background_tasks: BackgroundTasks
    ):
        # use the inference job id to recover the dataset record
        dataset_record = self._dataset_service._get_dataset_record_by_job_id(inference_job_id)

        # prepare the inputs for the evaluation job and pass the id of the new dataset
        job_eval_dict = {
            "name": f"{request.name}-evaluation",
            "model": request.model,
            "dataset": dataset_record.id,
            "max_samples": request.max_samples,
            "skip_inference": True,
        }

        # submit the job
        self._job_service.create_job(JobEvalCreate.model_validate(job_eval_dict), background_tasks)

        # TODO: do something with the job_response.id (e.g. add to the experiments' job list)

    def create_experiment(
        self, request: ExperimentCreate, background_tasks: BackgroundTasks
    ) -> ExperimentResponse:
        # input is ExperimentCreate, we need to split the configs and generate one
        # JobInferenceCreate and one JobEvalCreate
        job_inference_dict = {
            "name": f"{request.name}-inference",
            "model": request.model,
            "dataset": request.dataset,
            "max_samples": request.max_samples,
            "model_url": request.model_url,
            "system_prompt": request.system_prompt,
        }

        # submit inference job first
        job_response = self._job_service.create_job(
            JobInferenceCreate.model_validate(job_inference_dict), background_tasks
        )

        # run evaluation job afterwards
        # (NOTE: tasks in starlette are executed sequentially: https://www.starlette.io/background/)
        background_tasks.add_task(self._run_eval, job_response.id, request, background_tasks)

        return job_response
