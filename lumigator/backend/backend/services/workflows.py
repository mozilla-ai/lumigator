import asyncio
import numbers
from pathlib import Path
from uuid import UUID

import loguru
from fastapi import BackgroundTasks
from lumigator_schemas.jobs import (
    JobCreate,
    JobEvalConfig,
    JobInferenceConfig,
    JobLogsResponse,
    JobResultObject,
    JobStatus,
)
from lumigator_schemas.tasks import TextGenerationTaskDefinition
from lumigator_schemas.workflows import (
    WorkflowCreateRequest,
    WorkflowDetailsResponse,
    WorkflowResponse,
    WorkflowStatus,
)
from mlflow.entities import Run
from pydantic_core._pydantic_core import ValidationError
from typing_extensions import deprecated

from backend.repositories.jobs import JobRepository
from backend.services.datasets import DatasetService
from backend.services.exceptions.dataset_exceptions import (
    DatasetInvalidError,
    DatasetMissingFieldsError,
    DatasetNotFoundError,
    DatasetSizeError,
    DatasetUpstreamError,
)
from backend.services.exceptions.job_exceptions import (
    JobTypeUnsupportedError,
    JobUpstreamError,
)
from backend.services.exceptions.secret_exceptions import SecretNotFoundError
from backend.services.exceptions.tracking_exceptions import TrackingClientUpstreamError
from backend.services.exceptions.workflow_exceptions import (
    WorkflowDownloadNotAvailableError,
    WorkflowNotFoundError,
    WorkflowUpstreamError,
    WorkflowValidationError,
)
from backend.services.jobs import JobService
from backend.services.secrets import SecretExistenceChecker
from backend.settings import settings
from backend.tracking import TrackingClient
from backend.tracking.schemas import RunOutputs


class WorkflowService:
    def __init__(
        self,
        job_repo: JobRepository,
        job_service: JobService,
        dataset_service: DatasetService,
        background_tasks: BackgroundTasks,
        secret_checker: SecretExistenceChecker,
        tracking_client: TrackingClient,
    ):
        self._job_repo = job_repo
        self._job_service = job_service
        self._dataset_service = dataset_service
        self._tracking_client = tracking_client
        self._secret_checker = secret_checker
        self._background_tasks = background_tasks
        self.NON_TERMINAL_STATUS = [
            JobStatus.CREATED.value,
            JobStatus.PENDING.value,
            JobStatus.RUNNING.value,
        ]

        # TODO: rely on https://github.com/ray-project/ray/blob/7c2a200ef84f17418666dad43017a82f782596a3/python/ray/dashboard/modules/job/common.py#L53
        self.TERMINAL_STATUS = [JobStatus.FAILED.value, JobStatus.SUCCEEDED.value]

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

    async def _handle_workflow_failure(self, workflow_id: str):
        """Handle a workflow failure by updating the workflow status and stopping any running jobs."""
        loguru.logger.error("Workflow failed: {} ... updating status and stopping jobs", workflow_id)

        # Get the list of non-complete jobs in the workflow.
        async def non_terminal_jobs(jobs: list[Run]):
            for job in jobs:
                if not await self._tracking_client.is_status_terminal(job.info.status):
                    yield job

        workflow_jobs = await self._tracking_client.list_jobs(workflow_id)
        non_terminal_jobs = [job async for job in non_terminal_jobs(workflow_jobs)]

        # Create a list of tasks: Ray jobs to stop, and MLFlow runs to mark as failed.
        stop_tasks = [
            self._job_service.stop_job(UUID(ray_job_id))
            for job in non_terminal_jobs
            if (ray_job_id := job.data.params.get("ray_job_id"))
        ] + [
            self._tracking_client.update_workflow_status(run.info.run_id, WorkflowStatus.FAILED)
            for run in non_terminal_jobs
        ]

        # Wait for all tasks to complete concurrently (if we have any).
        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=False)

        # Finally, mark the parent workflow as failed.
        await self._tracking_client.update_workflow_status(workflow_id, WorkflowStatus.FAILED)

    async def _run_inference_eval_pipeline(
        self,
        workflow: WorkflowResponse,
        request: WorkflowCreateRequest,
    ):
        """Currently this is our only workflow. As we make this more flexible to handle different
        sequences of jobs, we'll need to refactor this function to be more generic.
        """
        experiment = await self._tracking_client.get_experiment(request.experiment_id)

        # input is WorkflowCreateRequest, we need to split the configs and generate one
        # JobInferenceCreate and one JobEvalCreate
        job_infer_config = JobInferenceConfig(
            model=request.model,
            provider=request.provider,
            base_url=request.base_url,
            output_field=request.inference_output_field,
            task_definition=experiment.task_definition,
            system_prompt=request.system_prompt,
            # we store the dataset explicitly below, so it gets queued before eval
            store_to_dataset=False,
            generation_config=request.generation_config,
            secret_key_name=request.secret_key_name,
        )
        job_infer_create = JobCreate(
            name=f"{request.name}-inference",
            dataset=experiment.dataset,
            max_samples=experiment.max_samples,
            batch_size=request.batch_size,
            job_config=job_infer_config,
        )

        try:
            # Attempt to submit the inference job to Ray before we track it in Lumigator.
            inference_job = self._job_service.create_job(job_infer_create)
        except (JobTypeUnsupportedError, SecretNotFoundError) as e:
            loguru.logger.error("Workflow pipeline error: Workflow {}. Cannot create inference job: {}", workflow.id, e)
            await self._handle_workflow_failure(workflow.id)
            return

        # Track the workflow status as running and add the inference job.
        await self._tracking_client.update_workflow_status(workflow.id, WorkflowStatus.RUNNING)
        inference_run_id = await self._tracking_client.create_job(
            request.experiment_id, workflow.id, "inference", inference_job.id
        )

        try:
            # Wait for the inference job to 'complete'.
            status = await self._job_service.wait_for_job_complete(
                inference_job.id, max_wait_time_sec=request.job_timeout_sec
            )

            if status != JobStatus.SUCCEEDED:
                # Trigger the failure handling logic
                raise JobUpstreamError(f"Inference job {inference_job.id} failed with status '{status}'") from None

            # Mark the job as successful in the tracking client.
            await self._tracking_client.update_workflow_status(inference_run_id, WorkflowStatus.SUCCEEDED)
        except JobUpstreamError as e:
            loguru.logger.error(
                "Workflow pipeline error: Workflow {}. Inference job: {} failed: {}", workflow.id, inference_job.id, e
            )
            await self._handle_workflow_failure(workflow.id)
            return

        try:
            # Figure out the dataset filename
            request_dataset = self._dataset_service.get_dataset(dataset_id=experiment.dataset)
            dataset_filename = request_dataset.filename
            dataset_filename = Path(dataset_filename).stem
            dataset_filename = f"{dataset_filename}-{request.model.replace('/', '-')}-predictions.csv"
        except DatasetNotFoundError as e:
            loguru.logger.error(
                "Workflow pipeline error: Workflow {}. Inference job: {}. Cannot compute dataset filename: {}",
                workflow.id,
                inference_job.id,
                e,
            )
            await self._handle_workflow_failure(workflow.id)
            return

        try:
            # Inference jobs produce a new dataset
            # Add the dataset to the (local) database
            inference_dataset_id = self._job_service._add_dataset_to_db(
                job_id=inference_job.id,
                request=job_infer_create,
                s3_file_system=self._dataset_service.s3_filesystem,
                dataset_filename=dataset_filename,
                is_gt_generated=request_dataset.generated,
            )
        except (
            DatasetNotFoundError,
            DatasetSizeError,
            DatasetInvalidError,
            DatasetMissingFieldsError,
            DatasetUpstreamError,
        ) as e:
            loguru.logger.error(
                "Workflow pipeline error: Workflow {}. Inference job: {}. Cannot update DB with with result data: {}",
                workflow.id,
                inference_job.id,
                e,
            )
            await self._handle_workflow_failure(workflow.id)
            return

        try:
            # log the job to the tracking client
            # TODO: Review how JobService._get_s3_uri works and if it can be re-used/made public.
            inference_results_path = self._job_service._get_s3_uri(inference_job.id)

            with self._dataset_service.s3_filesystem.open(inference_results_path, "r") as f:
                inf_output = JobResultObject.model_validate_json(f.read())

            inference_job_output = RunOutputs(
                parameters={"inference_output_s3_path": inference_results_path},
                metrics=inf_output.metrics,
                ray_job_id=str(inference_job.id),
            )
            await self._tracking_client.update_job(inference_run_id, inference_job_output)
        except Exception as e:
            loguru.logger.error(
                "Workflow pipeline error: Workflow {}. Inference job: {}. Cannot update DB with with result data: {}",
                workflow.id,
                inference_job.id,
                e,
            )
            await self._handle_workflow_failure(workflow.id)
            return

        # FIXME The ray status is now _not enough_ to set the job status,

        job_eval_config = JobEvalConfig(task_definition=experiment.task_definition)

        # if some custom parameters are provided for evaluation (e.g. special metrics
        # such as those based on g-eval), bring them over to the job
        if request.metrics:
            job_eval_config.metrics = request.metrics

            if request.llm_as_judge:
                # if params for local model in llm-as-judge are provided, bring them over
                # (and ignore any API keys because they are not required for ollama/local models)
                job_eval_config.llm_as_judge = request.llm_as_judge
            else:
                if any(s.startswith("g_eval_") for s in job_eval_config.metrics):
                    job_eval_config.secret_key_name = "openai_api_key"  # pragma: allowlist secret

        # prepare the inputs for the evaluation job and pass the id of the new dataset
        job_eval_create = JobCreate(
            name=f"{request.name}-evaluation",
            dataset=inference_dataset_id,
            max_samples=experiment.max_samples,
            job_config=job_eval_config,
        )

        try:
            # Attempt to submit the evaluation job before we track it in Lumigator.
            evaluation_job = self._job_service.create_job(job_eval_create)
        except (JobTypeUnsupportedError, SecretNotFoundError) as e:
            loguru.logger.error(
                "Workflow pipeline error: Workflow {}. Cannot create evaluation job: {}", workflow.id, e
            )
            await self._handle_workflow_failure(workflow.id)
            return

        # Track the evaluation job.
        eval_run_id = await self._tracking_client.create_job(
            experiment_id=request.experiment_id,
            workflow_id=workflow.id,
            name="evaluation",
            job_id=evaluation_job.id,
        )

        try:
            # wait for the evaluation job to complete
            status = await self._job_service.wait_for_job_complete(
                evaluation_job.id, max_wait_time_sec=request.job_timeout_sec
            )

            if status != JobStatus.SUCCEEDED:
                # Trigger the failure handling logic
                raise JobUpstreamError(f"Evaluation job {evaluation_job.id} failed with status '{status}'") from None

            # TODO: Handle other error types that can be raised by the method.
            self._job_service._validate_results(evaluation_job.id, self._dataset_service.s3_filesystem)

            # Mark the job as successful in the tracking client.
            await self._tracking_client.update_workflow_status(eval_run_id, WorkflowStatus.SUCCEEDED)
        except (JobUpstreamError, ValidationError) as e:
            loguru.logger.error(
                "Workflow pipeline error: Workflow {}. Evaluation job: {} failed: {}", workflow.id, evaluation_job.id, e
            )
            await self._handle_workflow_failure(workflow.id)
            return

        try:
            loguru.logger.info(
                "Workflow pipeline: Workflow {}. Evaluation job: {}. Handling evaluation result",
                workflow.id,
                evaluation_job,
            )

            # Get the path to the job results stored in S3.
            evaluation_result_path = self._job_service._get_s3_uri(evaluation_job.id)

            with self._dataset_service.s3_filesystem.open(evaluation_result_path, "r") as f:
                eval_output = JobResultObject.model_validate_json(f.read())

            # TODO this generic interface should probably be the output type of the eval job but
            # we'll make that improvement later

            formatted_metrics = self._prepare_metrics(eval_output)

            outputs = RunOutputs(
                metrics=formatted_metrics,
                # eventually this could be an artifact and be stored by the tracking client,
                #  but we'll keep it as being stored the way it is for right now.
                parameters={"eval_output_s3_path": evaluation_result_path},
                ray_job_id=str(evaluation_job.id),
            )
            await self._tracking_client.update_job(eval_run_id, outputs)
        except Exception as e:
            loguru.logger.error(
                "Workflow pipeline error: Workflow {}. Evaluation job: {} Error validating results: {}",
                workflow.id,
                evaluation_job.id,
                e,
            )
            await self._handle_workflow_failure(workflow.id)
            return

        try:
            await self._tracking_client.update_workflow_status(workflow.id, WorkflowStatus.SUCCEEDED)
            await self._tracking_client.get_workflow(workflow.id)
        except Exception as e:
            loguru.logger.error(
                "Workflow pipeline error: Workflow {}. Error updating completed workflow: {}",
                workflow.id,
                e,
            )

    async def get_workflow_result_download(self, workflow_id: str) -> str:
        """Return workflow results file URL for downloading.

        Args:
            workflow_id: ID of the workflow whose results will be returned
        """
        workflow_details = await self.get_workflow(workflow_id)
        if workflow_details.artifacts_download_url:
            return workflow_details.artifacts_download_url
        else:
            raise WorkflowDownloadNotAvailableError(workflow_id) from None

    async def get_workflow(self, workflow_id: str) -> WorkflowDetailsResponse:
        """Get a workflow.

        :param workflow_id: The ID of the workflow to retrieve.
        :return: The workflow details.
        :raises WorkflowNotFoundError: If the workflow is not found.
        :raises WorkflowUpstreamError: If there is an error retrieving the workflow from the tracking client.
        """
        try:
            tracking_server_workflow = await self._tracking_client.get_workflow(workflow_id)
        except TrackingClientUpstreamError as e:
            raise WorkflowUpstreamError("mlflow", f"Workflow: {workflow_id}, Error getting workflow.") from e

        if tracking_server_workflow is None:
            raise WorkflowNotFoundError(workflow_id) from None

        return tracking_server_workflow

    async def create_workflow(self, request: WorkflowCreateRequest) -> WorkflowResponse:
        """Creates a new workflow and submits inference and evaluation jobs.

        Args:
            request (WorkflowCreateRequest): The request containing the workflow configuration.

        Returns:
            WorkflowResponse: The response object containing the details of the created workflow.
        """
        # If the experiment this workflow is associated with doesn't exist, there's no point in continuing.
        experiment = await self._tracking_client.get_experiment(request.experiment_id)
        if not experiment:
            raise WorkflowValidationError(f"Cannot create workflow '{request.name}': No experiment found.") from None

        # If we need a secret key that doesn't exist in Lumigator, there's no point in continuing.
        if request.secret_key_name and not self._secret_checker.is_secret_configured(request.secret_key_name):
            raise WorkflowValidationError(
                f"Cannot create workflow '{request.name}' for experiment '{experiment.name}': "
                f"Requested secret key '{request.secret_key_name}' is not configured."
            ) from None

        loguru.logger.info(f"Creating workflow '{request.name}' for experiment ID '{request.experiment_id}'")

        if experiment.task_definition == TextGenerationTaskDefinition() and not request.system_prompt:
            raise WorkflowValidationError("Default system_prompt not available for text-generation") from None

        if request.system_prompt:
            loguru.logger.info(f"Using system prompt: {request.system_prompt}")
        else:
            default_system_prompt = settings.get_default_system_prompt(experiment.task_definition)
            loguru.logger.warning(
                f"System prompt not provided. Using default system prompt: '{default_system_prompt}'. "
                "This may not be optimal for your task."
            )
            request.system_prompt = default_system_prompt

        workflow = await self._tracking_client.create_workflow(
            experiment_id=request.experiment_id,
            description=request.description,
            name=request.name,
            model=request.model,
            system_prompt=request.system_prompt,
            # input is WorkflowCreate, we need to split the configs and generate one
            # JobInferenceCreate and one JobEvalCreate
        )

        # Run the inference and evaluation pipeline as a background task
        self._background_tasks.add_task(self._run_inference_eval_pipeline, workflow, request)

        return workflow

    async def delete_workflow(self, workflow_id: str, force: bool) -> WorkflowResponse:
        """Delete a workflow by ID."""
        # if the workflow is running, we should throw an error
        workflow = await self.get_workflow(workflow_id)
        if workflow.status == WorkflowStatus.RUNNING and not force:
            raise WorkflowValidationError("Cannot delete a running workflow")
        return await self._tracking_client.delete_workflow(workflow_id)

    @deprecated("get_workflow_logs is deprecated, it will be removed in future versions.")
    async def get_workflow_logs(self, workflow_id: str) -> JobLogsResponse:
        """Get the logs for a workflow."""
        job_list = await self._tracking_client.list_jobs(workflow_id)
        # sort the jobs by created_at, with the oldest last
        job_list = sorted(job_list, key=lambda x: x.info.start_time)
        all_ray_job_ids = [run.data.params.get("ray_job_id") for run in job_list]
        logs = [self._job_service.get_job_logs(UUID(ray_job_id)) for ray_job_id in all_ray_job_ids]
        # combine the logs into a single string
        # TODO: This is not a great solution but it matches the current API
        return JobLogsResponse(logs="\n================\n".join([log.logs for log in logs]))
