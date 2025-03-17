import asyncio
import json
import numbers
from pathlib import Path
from uuid import UUID

import loguru
from fastapi import BackgroundTasks
from lumigator_schemas.jobs import (
    JobLogsResponse,
    JobResultObject,
    JobStatus,
)
from lumigator_schemas.workflows import (
    WorkflowCreateRequest,
    WorkflowDetailsResponse,
    WorkflowJobsCreateRequest,
    WorkflowResponse,
    WorkflowStatus,
)

from backend.repositories.jobs import JobRepository
from backend.services.datasets import DatasetService
from backend.services.exceptions.job_exceptions import (
    JobUpstreamError,
)
from backend.services.exceptions.workflow_exceptions import (
    WorkflowNotFoundError,
    WorkflowValidationError,
)
from backend.services.jobs import JOB_STOP_WAIT, JobService
from backend.settings import settings
from backend.tracking import TrackingClient
from backend.tracking.schemas import RunOutputs


class JobsWorkflowService:
    def __init__(
        self,
        job_repo: JobRepository,
        job_service: JobService,
        dataset_service: DatasetService,
        background_tasks: BackgroundTasks,
        tracking_client: TrackingClient,
    ):
        self._job_repo = job_repo
        self._job_service = job_service
        self._dataset_service = dataset_service
        self._tracking_client = tracking_client
        self._background_tasks = background_tasks
        self.NON_TERMINAL_STATUS = [
            JobStatus.CREATED,
            JobStatus.PENDING,
            JobStatus.RUNNING,
        ]
        self._tasks = dict()

        # TODO: rely on https://github.com/ray-project/ray/blob/7c2a200ef84f17418666dad43017a82f782596a3/python/ray/dashboard/modules/job/common.py#L53
        self.TERMINAL_STATUS = [JobStatus.FAILED, JobStatus.SUCCEEDED]

    def _prepare_metrics(self, eval_output: JobResultObject) -> dict:
        """Flatten the metrics dictionary to a single level so that it can be stored in RunOutputs."""
        formatted_metrics = {}
        for metric_name, metric_value in eval_output.metrics.items():
            if isinstance(metric_value, dict):
                for sub_metric_name, sub_metric_value in metric_value.items():
                    # only interested in mean, so we only look it items that are not lists
                    if isinstance(sub_metric_value, numbers.Number) and sub_metric_value is not None:
                        formatted_metrics[f"{metric_name}_{sub_metric_name}"] = round(sub_metric_value, 3)
            elif isinstance(metric_value, numbers.Number) and metric_value is not None:
                formatted_metrics[metric_name] = round(metric_value, 3)
        return formatted_metrics

    async def _run_job(
        self,
        request: WorkflowJobsCreateRequest,
    ) -> WorkflowResponse:
        pass

    def _add_background_task(self, background_tasks: BackgroundTasks, task: callable, *args):
        """Adds a background task to the background tasks queue."""
        # background_tasks.add_task(task, *args)
        # First arg in *args will be taken as the job id
        backtask = asyncio.create_task(task(*args))
        id = args[0].id
        self._tasks[id] = backtask
        backtask.add_done_callback(lambda: self._tasks.pop(id, None))

    async def _run_pipeline(
        self,
        workflow: WorkflowResponse,
        request: WorkflowJobsCreateRequest,
    ):
        """Currently this is our only workflow. As we make this more flexible to handle different
        sequences of jobs, we'll need to refactor this function to be more generic.
        """
        # input is WorkflowCreateRequest, we need to split the configs and generate one
        # JobInferenceCreate and one JobEvalCreate
        # workflow has now started!
        self._tracking_client.update_workflow_status(workflow.id, WorkflowStatus.RUNNING)
        # TODO Currently we will use a single dataset var to hold
        # the pointer to the result of the previous stage
        # A more flexible implementation could use a dict[job.name, dataset] for example
        # and use an "input_dataset" field in the current job
        # Initially the dataset is the workflow dataset
        previous_dataset_record = request.dataset
        try:
            for job_index, job in enumerate(request.job_list):
                loguru.logger.critical(f"--> Acting on dataset: {previous_dataset_record}, name: {job.name}")
                # $ref resolution, to refactor
                if job_index == 0:
                    job.job_config.model = workflow.model

                job.dataset = previous_dataset_record
                loguru.logger.critical("--> 1:")
                # Doesn't seem necessary
                # ??? self._job_service._validate_results(evaluation_job.id, self._dataset_service.s3_filesystem)
                job_response = self._job_service.create_job(job)
                job_run_id = self._tracking_client.create_job(
                    request.experiment_id, workflow.id, job.job_config.job_type.value, job_response.id
                )
                loguru.logger.critical("--> 2:")
                status = await self._job_service.wait_for_job_finished(
                    job_response.id, max_wait_time_sec=request.job_timeout_sec
                )
                loguru.logger.critical(f"--> 2: Job {job_response.id} finally finished")
                if JobStatus(status) in JobService.TERMINAL_STATUS:
                    if status != JobStatus.SUCCEEDED:
                        loguru.logger.error(f"Job {job_response.id} did not succeed with status {status}")
                        raise Exception(f"Job {job_response.id} did not succeed with status {status}")
                else:
                    try:
                        self._job_service._stop_job(job_response.id)
                        status = await self._job_service.wait_for_job_finished(
                            job_response.id, max_wait_time_sec=JOB_STOP_WAIT
                        )
                    except JobUpstreamError:
                        loguru.logger.error(f"Failed to stop job {job_response.id}, continuing")
                    raise Exception(f"Job {job_response.id} did not reach terminal state, current status {status}")
                # log the job to the tracking client
                loguru.logger.critical("--> 3:")
                result_key = str(
                    Path(settings.S3_JOB_RESULTS_PREFIX)
                    / settings.S3_JOB_RESULTS_FILENAME.format(job_name=job.name, job_id=job_response.id)
                )
                dataset_path = self._dataset_service._get_s3_path(result_key)
                with self._dataset_service.s3_filesystem.open(dataset_path, "r") as f:
                    job_output = JobResultObject.model_validate(json.loads(f.read()))
                output_path = f"{settings.S3_BUCKET}/{self._job_service._get_results_s3_key(job_response.id)}"
                # FIXME Check if this can be done with inference results
                loguru.logger.critical("--> 4:")
                formatted_metrics = self._prepare_metrics(job_output)
                job_output = RunOutputs(
                    metrics=formatted_metrics,
                    parameters={"job_output_s3_path": output_path},
                    ray_job_id=str(job_response.id),
                )

                self._tracking_client.update_job(job_run_id, job_output)
                result_dataset = self._dataset_service._get_dataset_record_by_job_id(job_response.id)
                if result_dataset:
                    previous_dataset_record = result_dataset.id
                else:
                    previous_dataset_record = None
        except Exception as e:
            loguru.logger.critical(f"Workflow {request.name} for experiment {request.experiment_id} failed: {e}")
            await self._handle_workflow_failure(workflow.id)
        self._tracking_client.update_workflow_status(workflow.id, WorkflowStatus.SUCCEEDED)

    async def _handle_workflow_failure(self, workflow_id: str):
        """Handle a workflow failure by updating the workflow status."""
        loguru.logger.error("Workflow failed: {} ... updating status", workflow_id)

        # Mark the workflow as failed.
        self._tracking_client.update_workflow_status(workflow_id, WorkflowStatus.FAILED)

    def get_workflow(self, workflow_id: str) -> WorkflowDetailsResponse:
        """Get a workflow."""
        tracking_server_workflow = self._tracking_client.get_workflow(workflow_id)
        if tracking_server_workflow is None:
            raise WorkflowNotFoundError(workflow_id) from None
        return tracking_server_workflow

    def create_workflow(self, request: WorkflowCreateRequest) -> WorkflowResponse:
        """Creates a new workflow and submits inference and evaluation jobs.

        Args:
            request (WorkflowCreateRequest): The request containing the workflow configuration.

        Returns:
            WorkflowResponse: The response object containing the details of the created workflow.
        """
        loguru.logger.info(f"Creating workflow '{request.name}' for experiment ID '{request.experiment_id}'.")
        loguru.logger.critical(f"--> task queue: {self._tasks.keys()}")

        workflow = self._tracking_client.create_workflow(
            experiment_id=request.experiment_id,
            description=request.description,
            name=request.name,
            model=request.model,
            system_prompt=str(
                request.job_list[0].job_config.system_prompt
            ),  # FIXME where should we place the system prompt?
            # input is WorkflowCreate, we need to split the configs and generate one
            # JobInferenceCreate and one JobEvalCreate
        )

        self._add_background_task(self._background_tasks, self._run_pipeline, workflow, request)

        return workflow

    def delete_workflow(self, workflow_id: str, force: bool) -> WorkflowResponse:
        """Delete a workflow by ID."""
        # if the workflow is running, we should throw an error
        workflow = self.get_workflow(workflow_id)
        if workflow.status == WorkflowStatus.RUNNING and not force:
            raise WorkflowValidationError("Cannot delete a running workflow")
        return self._tracking_client.delete_workflow(workflow_id)

    def get_workflow_logs(self, workflow_id: str) -> JobLogsResponse:
        """Get the logs for a workflow."""
        job_list = self._tracking_client.list_jobs(workflow_id)
        # sort the jobs by created_at, with the oldest last
        job_list = sorted(job_list, key=lambda x: x.info.start_time)
        all_ray_job_ids = [run.data.params.get("ray_job_id") for run in job_list]
        logs = [self._job_service.get_job_logs(UUID(ray_job_id)) for ray_job_id in all_ray_job_ids]
        # combine the logs into a single string
        # TODO: This is not a great solution but it matches the current API
        return JobLogsResponse(logs="\n================\n".join([log.logs for log in logs]))
