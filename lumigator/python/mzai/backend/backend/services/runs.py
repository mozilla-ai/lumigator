import asyncio
import datetime
import uuid
from collections.abc import Callable
from uuid import UUID

import loguru
from fastapi import BackgroundTasks, HTTPException, status
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    JobEvalLiteCreate,
    JobInferenceCreate,
    JobStatus,
)
from lumigator_schemas.runs import RunCreate, RunResponse

from backend.records.experiments import ExperimentRecord
from backend.records.jobs import JobRecord
from backend.repositories.experiments import ExperimentRepository
from backend.repositories.jobs import JobRepository
from backend.services.datasets import DatasetService
from backend.services.jobs import JobService


class RunService:
    def __init__(
        self,
        experiment_repo: ExperimentRepository,
        job_repo: JobRepository,
        job_service: JobService,
        dataset_service: DatasetService,
    ):
        self._experiment_repo = experiment_repo
        self._job_repo = job_repo
        self._job_service = job_service
        self._dataset_service = dataset_service

    def _raise_not_found(self, job_id: UUID):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Job {job_id} not found.")

    def _get_experiment_record(self, experiment_id: UUID) -> ExperimentRecord:
        record = self._experiment_repo.get(experiment_id)
        if record is None:
            self._raise_not_found(experiment_id)
        return record

    def _get_jobs(self, experiment_id: UUID) -> list[JobRecord]:
        return self._job_repo.get_by_experiment_id(experiment_id)

    def get_jobs(self, experiment_id: UUID) -> ListingResponse[UUID]:
        """Return the list of job IDs created for a given experiment."""
        jobs = [job.id for job in self._get_jobs(experiment_id)]
        return ListingResponse[UUID].model_validate({"total": len(jobs), "items": jobs})

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
        request: RunCreate,
        background_tasks: BackgroundTasks,
        experiment_id: UUID = None,
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
            experiment_id=experiment_id,
        )

    def create_run(self, request: RunCreate, background_tasks: BackgroundTasks) -> RunResponse:
        """Creates a new run and submits inference and evaluation jobs.

        Args:
            request (RunCreate): The request object containing the run configuration.
            background_tasks (BackgroundTasks): The background tasks manager for scheduling tasks.

        Returns:
            RunResponse: The response object containing the details of the created run.
        """
        loguru.logger.info(
            f"Creating run '{request.name}' for experiment ID '{request.experiment_id}'."
        )

        # TODO create a new run object which will be stored in by the tracking service (aka mlflow)
        # right now just generate a random uuid
        created_at = datetime.datetime.now()

        run_record = {
            "id": uuid.uuid4(),
            "name": request.name,
            "description": request.description,
            "created_at": created_at,
            "updated_at": created_at,
        }

        # input is RunCreate, we need to split the configs and generate one
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
            experiment_id=request.experiment_id,
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
            request.experiment_id,
        )

        # TODO: This part will need to be refactored more: once everything is done, the last
        # step is to created two nested runs inside the run_record
        # which store the inference and evaluation job output info
        # on_job_complete_store_in_tracking_service()....
        run_record["status"] = JobStatus.CREATED

        return RunResponse.model_validate(run_record)

    def get_run(self, run_id: UUID) -> RunResponse:
        record = self._get_experiment_record(run_id)
        loguru.logger.info(f"Obtaining info for experiment {run_id}: {record}")

        all_succeeded = True
        for job in self._get_jobs(run_id):
            loguru.logger.info(f"Checking sub job: {job}")
            if self._job_service.get_job(job.id).status != JobStatus.SUCCEEDED:
                all_succeeded = False
                break

        if all_succeeded:
            record = self._experiment_repo.update(run_id, status=JobStatus.SUCCEEDED)

        return RunResponse.model_validate(record)
