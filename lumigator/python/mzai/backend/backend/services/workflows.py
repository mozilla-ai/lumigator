import asyncio
import datetime
import json
from collections.abc import Callable
from pathlib import Path
from uuid import UUID

import loguru
from evaluator_lite.schemas import EvalJobOutput
from fastapi import BackgroundTasks
from lumigator_schemas.jobs import (
    JobEvalLiteCreate,
    JobInferenceCreate,
    JobStatus,
)
from lumigator_schemas.workflows import WorkflowCreate, WorkflowResponse
from s3fs import S3FileSystem

from backend.repositories.experiments import ExperimentRepository
from backend.repositories.jobs import JobRepository
from backend.services.datasets import DatasetService
from backend.services.jobs import JobService
from backend.settings import settings
from backend.tracking import TrackingClient


class WorkflowService:
    def __init__(
        self,
        experiment_repo: ExperimentRepository,
        job_repo: JobRepository,
        job_service: JobService,
        dataset_service: DatasetService,
        tracking_client: TrackingClient,
    ):
        self._experiment_repo = experiment_repo
        self._job_repo = job_repo
        self._job_service = job_service
        self._dataset_service = dataset_service
        self._tracking_client = tracking_client

    async def on_job_complete(
        self, job_id: UUID, experiment_id: UUID, workflow_id: UUID, task: Callable = None, *args
    ):
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

    def _validate_evaluation_results(
        self,
        experiment_id: str,
        workflow_id: str,
        job_id: UUID,
        request: JobEvalLiteCreate,
        s3: S3FileSystem,
    ):
        """Handles the evaluation result for a given job.

        Args:
            job_id (UUID): The unique identifier of the job.
            request (JobEvalLiteCreate): The request object containing job evaluation details.
            s3 (S3FileSystem): The S3 file system object used to interact with the S3 bucket.

        Note:
            Currently, this function only validates the evaluation result. Future implementations
            may include storing the results in a database (e.g., mlflow).
        """
        loguru.logger.info("Handling evaluation result")

        result_key = str(
            Path(settings.S3_JOB_RESULTS_PREFIX)
            / settings.S3_JOB_RESULTS_FILENAME.format(job_name=request.name, job_id=job_id)
        )
        with s3.open(f"{settings.S3_BUCKET}/{result_key}", "r") as f:
            eval_output = EvalJobOutput.model_validate(json.loads(f.read()))
        self._tracking_client.log_run(experiment_id, workflow_id, eval_output)

    def _run_eval(
        self,
        inference_job_id: UUID,
        request: WorkflowCreate,
        background_tasks: BackgroundTasks,
        experiment_id: UUID,
        workflow_id: UUID,
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
        record = self._job_service.create_job(
            JobEvalLiteCreate.model_validate(job_eval_dict),
            background_tasks,
            experiment_id=experiment_id,
        )
        background_tasks.add_task(
            self.on_job_complete,
            record.id,
            experiment_id,
            workflow_id,
            self._validate_evaluation_results,
            experiment_id,
            workflow_id,
            record.id,
            JobEvalLiteCreate.model_validate(job_eval_dict),
            self._dataset_service.s3_filesystem,
        )

    def create_workflow(
        self, request: WorkflowCreate, background_tasks: BackgroundTasks
    ) -> WorkflowResponse:
        """Creates a new workflow and submits inference and evaluation jobs.

        Args:
            request (WorkflowCreate): The request object containing the workflow configuration.
            background_tasks (BackgroundTasks): The background tasks manager for scheduling tasks.

        Returns:
            WorkflowResponse: The response object containing the details of the created workflow.
        """
        loguru.logger.info(
            f"Creating workflow '{request.name}' for experiment ID '{request.experiment_id}'."
        )

        workflow_id = self._tracking_client.create_workflow(experiment_id=request.experiment_id)

        # input is WorkflowCreate, we need to split the configs and generate one
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
            request.experiment_id,
            workflow_id,
            self._run_eval,
            job_response.id,
            request,
            background_tasks,
            request.experiment_id,
            workflow_id,
        )

        # TODO create a new workflow object which will be stored in
        # by the tracking service (aka mlflow)
        created_at = datetime.datetime.now()
        # TODO right now this workflow_record is not related to the experiment,
        # but the 2 jobs created by the workflow are both associated with the experiment,
        # which is how we'll retrieve them until we
        # have implemented the association of workflows with experiments
        workflow_record = {
            "id": workflow_id,
            "name": request.name,
            "description": request.description,
            "created_at": created_at,
            "updated_at": created_at,
        }

        # TODO: This part will need to be refactored more:
        # once all the jobs are done, the last
        # step is to created two jobs inside the workflow_record
        # which store the inference and evaluation job output info
        # on_job_complete_store_in_tracking_client()....
        workflow_record["status"] = JobStatus.CREATED

        return WorkflowResponse.model_validate(workflow_record)
