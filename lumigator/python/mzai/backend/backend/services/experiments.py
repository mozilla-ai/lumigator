import asyncio
from collections.abc import Callable
from uuid import UUID

import loguru
from fastapi import BackgroundTasks
from lumigator_schemas.experiments import ExperimentCreate, ExperimentResponse
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    JobEvalLiteCreate,
    JobInferenceCreate,
    JobStatus,
)

from backend.repositories.experiments import ExperimentRepository
from backend.services.datasets import DatasetService
from backend.services.jobs import JobService


class ExperimentService:
    def __init__(
        self,
        experiment_repo: ExperimentRepository,
        job_service: JobService,
        dataset_service: DatasetService,
    ):
        self._experiment_repo = experiment_repo
        self._job_service = job_service
        self._dataset_service = dataset_service

    async def on_job_complete(self, job_id: UUID, task: Callable = None, *args):
        """Watches a submitted job and, when it terminates successfully, runs a given task.

        Inputs:
        - job_id: the UUID of the job to watch
        - task: the function to be called after the job completes successfully
        - args: the arguments to be passed to the function `task()`
        """
        job_status = self._job_service.ray_client.get_job_status(job_id)

        # TODO rely on https://github.com/ray-project/ray/blob/7c2a200ef84f17418666dad43017a82f782596a3/python/ray/dashboard/modules/job/common.py#L53
        valid_status = [
            JobStatus.CREATED.value.lower(),
            JobStatus.PENDING.value.lower(),
            JobStatus.RUNNING.value.lower(),
        ]
        stop_status = [JobStatus.FAILED.value.lower(), JobStatus.SUCCEEDED.value.lower()]

        loguru.logger.info(f"Watching {job_id}")
        while job_status.lower() not in stop_status and job_status.lower() in valid_status:
            await asyncio.sleep(5)
            job_status = self._job_service.ray_client.get_job_status(job_id)

        if job_status.lower() == JobStatus.FAILED.value.lower():
            loguru.logger.error(f"Job {job_id} failed: not running task {str(task)}")

        if job_status.lower() == JobStatus.SUCCEEDED.value.lower():
            loguru.logger.info(f"Job {job_id} finished successfully.")
            if task is not None:
                task(*args)

    def _run_eval(
        self,
        inference_job_id: UUID,
        request: ExperimentCreate,
        background_tasks: BackgroundTasks,
        experiment_id: UUID = None
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
        self._job_service.create_job(
            JobEvalLiteCreate.model_validate(job_eval_dict),
            background_tasks,
            experiment_id=experiment_id
        )

    def create_experiment(
        self, request: ExperimentCreate, background_tasks: BackgroundTasks
    ) -> ExperimentResponse:
        # The FastAPI BackgroundTasks object is used to run a function in the background.
        # It is a wrapper around Starlette's BackgroundTasks object.
        # A background task should be attached to a response,
        # and will run only once the response has been sent.
        # See here: https://www.starlette.io/background/

        experiment_record = self._experiment_repo.create(
            name=request.name, description=request.description
        )
        loguru.logger.info(f"Created experiment '{request.name}' with ID '{experiment_record.id}'.")

        # input is ExperimentCreate, we need to split the configs and generate one
        # JobInferenceCreate and one JobEvalCreate
        job_inference_dict = {
            "name": f"{request.name}-inference",
            "model": request.model,
            "dataset": request.dataset,
            "max_samples": request.max_samples,
            "model_url": request.model_url,
            "output_field": request.inference_output_field,
            "system_prompt": request.system_prompt,
            "store_to_dataset": True,
        }

        # submit inference job first
        job_response = self._job_service.create_job(
            JobInferenceCreate.model_validate(job_inference_dict),
            background_tasks,
            experiment_id=experiment_record.id,
        )

        # run evaluation job afterwards
        # (NOTE: tasks in starlette are executed sequentially: https://www.starlette.io/background/)
        background_tasks.add_task(
            self.on_job_complete,
            job_response.id,
            self._run_eval,
            job_response.id,
            request,
            background_tasks,
            experiment_record.id,
        )

        return ExperimentResponse.model_validate(experiment_record)

    def list_experiments(
        self, skip: int = 0, limit: int = 100
    ) -> ListingResponse[ExperimentResponse]:
        records = self._experiment_repo.list(skip, limit)
        return ListingResponse(
            total=self._experiment_repo.count(),
            items=[ExperimentResponse.model_validate(x) for x in records],
        )
