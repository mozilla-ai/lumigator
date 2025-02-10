import json
from pathlib import Path

import loguru
from fastapi import BackgroundTasks
from lumigator_schemas.jobs import (
    JobCreate,
    JobEvalLiteConfig,
    JobInferenceConfig,
    JobLogsResponse,
    JobResultObject,
    JobStatus,
)
from lumigator_schemas.workflows import (
    WorkflowCreateRequest,
    WorkflowDetailsResponse,
    WorkflowResponse,
    WorkflowStatus,
)

from backend.repositories.jobs import JobRepository
from backend.services.datasets import DatasetService
from backend.services.exceptions.workflow_exceptions import (
    WorkflowNotFoundError,
    WorkflowValidationError,
)
from backend.services.jobs import JobService
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
        tracking_client: TrackingClient,
    ):
        self._job_repo = job_repo
        self._job_service = job_service
        self._dataset_service = dataset_service
        self._tracking_client = tracking_client
        self._background_tasks = background_tasks
        self.NON_TERMINAL_STATUS = [
            JobStatus.CREATED.value,
            JobStatus.PENDING.value,
            JobStatus.RUNNING.value,
        ]

        # TODO: rely on https://github.com/ray-project/ray/blob/7c2a200ef84f17418666dad43017a82f782596a3/python/ray/dashboard/modules/job/common.py#L53
        self.TERMINAL_STATUS = [JobStatus.FAILED.value, JobStatus.SUCCEEDED.value]

    async def _run_inference_eval_pipeline(
        self,
        workflow: WorkflowResponse,
        request: WorkflowCreateRequest,
    ):
        """Currently this is our only "workflow. As we make this more flexible to handle different
        sequences of jobs, we'll need to refactor this function to be more generic.
        """
        # input is WorkflowCreateRequest, we need to split the configs and generate one
        # JobInferenceCreate and one JobEvalCreate
        job_infer_config = JobInferenceConfig(
            model=request.model,
            model_url=request.model_url,
            output_field=request.inference_output_field,
            system_prompt=request.system_prompt,
            store_to_dataset=True,
        )
        job_infer_create = JobCreate(
            name=f"{request.name}-inference",
            dataset=request.dataset,
            max_samples=request.max_samples,
            job_config=job_infer_config,
        )

        # submit inference job first
        inference_job = self._job_service.create_job(
            job_infer_create,
        )
        # workflow has now started!
        self._tracking_client.update_workflow_status(workflow.id, WorkflowStatus.RUNNING)

        # wait for the inference job to complete
        status = await self._job_service.wait_for_job_complete(
            inference_job.id, max_wait_time_sec=60 * 10
        )
        if status != JobStatus.SUCCEEDED:
            loguru.logger.error(f"Inference job {inference_job.id} failed")
            self._tracking_client.update_workflow_status(workflow.id, WorkflowStatus.FAILED)
            raise Exception(f"Inference job {inference_job.id} failed")

        # Inference jobs produce a new dataset
        # Add the dataset to the (local) database
        self._job_service._add_dataset_to_db(
            inference_job.id,
            job_infer_create,
            self._dataset_service.s3_filesystem,
        )
        # log the job to the tracking client
        inf_path = f"{settings.S3_BUCKET}/{self._job_service._get_results_s3_key(inference_job.id)}"
        inference_job_output = RunOutputs(
            parameters={"inference_output_s3_path": inf_path},
            ray_job_id=str(inference_job.id),
        )
        self._tracking_client.create_job(
            request.experiment_id, workflow.id, "inference", inference_job_output
        )

        # FIXME The ray status is now _not enough_ to set the job status,
        # use the inference job id to recover the dataset record
        dataset_record = self._dataset_service._get_dataset_record_by_job_id(inference_job.id)

        # prepare the inputs for the evaluation job and pass the id of the new dataset
        job_eval_create = JobCreate(
            name=f"{request.name}-evaluation",
            dataset=dataset_record.id,
            max_samples=request.max_samples,
            job_config=JobEvalLiteConfig(),
        )

        # submit the job
        evaluation_job = self._job_service.create_job(
            job_eval_create,
        )

        # wait for the evaluation job to complete
        status = await self._job_service.wait_for_job_complete(
            evaluation_job.id, max_wait_time_sec=60 * 10
        )
        self._job_service._validate_results(evaluation_job.id, self._dataset_service.s3_filesystem)
        if status != JobStatus.SUCCEEDED:
            loguru.logger.error(f"Evaluation job {evaluation_job.id} failed")
            self._tracking_client.update_workflow_status(workflow.id, WorkflowStatus.FAILED)
        try:
            loguru.logger.info("Handling evaluation result")

            result_key = str(
                Path(settings.S3_JOB_RESULTS_PREFIX)
                / settings.S3_JOB_RESULTS_FILENAME.format(
                    job_name=job_eval_create.name, job_id=evaluation_job.id
                )
            )
            with self._dataset_service.s3_filesystem.open(
                f"{settings.S3_BUCKET}/{result_key}", "r"
            ) as f:
                eval_output = JobResultObject.model_validate(json.loads(f.read()))

            # TODO this generic interface should probably be the output type of the eval job but
            # we'll make that improvement later
            # Get the dataset from the S3 bucket
            result_key = self._job_service._get_results_s3_key(evaluation_job.id)

            outputs = RunOutputs(
                metrics={
                    "rouge1_mean": round(eval_output.metrics["rouge"]["rouge1_mean"], 3),
                    "rouge2_mean": round(eval_output.metrics["rouge"]["rouge2_mean"], 3),
                    "rougeL_mean": round(eval_output.metrics["rouge"]["rougeL_mean"], 3),
                    "rougeLsum_mean": round(eval_output.metrics["rouge"]["rougeLsum_mean"], 3),
                    "bertscore_f1_mean": round(eval_output.metrics["bertscore"]["f1_mean"], 3),
                    "bertscore_precision_mean": round(
                        eval_output.metrics["bertscore"]["precision_mean"], 3
                    ),
                    "bertscore_recall_mean": round(
                        eval_output.metrics["bertscore"]["recall_mean"], 3
                    ),
                    "meteor_mean": round(eval_output.metrics["meteor"]["meteor_mean"], 3),
                },
                # eventually this could be an artifact and be stored by the tracking client,
                #  but we'll keep it as being stored the way it is for right now.
                parameters={"eval_output_s3_path": f"{settings.S3_BUCKET}/{result_key}"},
                ray_job_id=str(evaluation_job.id),
            )
            self._tracking_client.create_job(
                request.experiment_id, workflow.id, "evaluation", outputs
            )
            self._tracking_client.update_workflow_status(workflow.id, WorkflowStatus.SUCCEEDED)
        except Exception as e:
            loguru.logger.error(f"Error validating evaluation results: {e}")
            self._tracking_client.update_workflow_status(workflow.id, WorkflowStatus.FAILED)

    def get_workflow(self, workflow_id: str) -> WorkflowDetailsResponse:
        """Get a workflow."""
        tracking_server_workflow = self._tracking_client.get_workflow(workflow_id)
        if tracking_server_workflow is None:
            raise WorkflowNotFoundError(workflow_id)
        return tracking_server_workflow

    def create_workflow(self, request: WorkflowCreateRequest) -> WorkflowResponse:
        """Creates a new workflow and submits inference and evaluation jobs.

        Args:
            request (WorkflowCreateRequest): The request containing the workflow configuration.

        Returns:
            WorkflowResponse: The response object containing the details of the created workflow.
        """
        loguru.logger.info(
            f"Creating workflow '{request.name}' for experiment ID '{request.experiment_id}'."
        )

        workflow = self._tracking_client.create_workflow(
            experiment_id=request.experiment_id,
            description=request.description,
            name=request.name,
            # input is WorkflowCreate, we need to split the configs and generate one
            # JobInferenceCreate and one JobEvalCreate
        )

        # Run the inference and evaluation pipeline as a background task
        self._background_tasks.add_task(self._run_inference_eval_pipeline, workflow, request)

        return workflow

    def delete_workflow(self, workflow_id: str) -> WorkflowResponse:
        """Delete a workflow by ID."""
        # if the workflow is running, we should throw an error
        workflow = self.get_workflow(workflow_id)
        if workflow.status == WorkflowStatus.RUNNING:
            raise WorkflowValidationError("Cannot delete a running workflow")
        return self._tracking_client.delete_workflow(workflow_id)

    def get_workflow_logs(self, workflow_id: str) -> JobLogsResponse:
        """Get the logs for a workflow."""
        return self._tracking_client.get_workflow_logs(workflow_id)
