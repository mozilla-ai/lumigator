import json
from pathlib import Path

import loguru
from evaluator_lite.schemas import EvalJobOutput
from fastapi import BackgroundTasks
from lumigator_schemas.extras import ListingResponse
from lumigator_schemas.jobs import (
    JobEvalLiteCreate,
    JobInferenceCreate,
    JobResponse,
    JobStatus,
)
from lumigator_schemas.workflows import (
    WorkflowCreateRequest,
    WorkflowDetailsResponse,
    WorkflowResponse,
    WorkflowResultDownloadResponse,
    WorkflowStatus,
)
from s3fs import S3FileSystem

from backend.repositories.jobs import JobRepository
from backend.services.datasets import DatasetService
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
        tracking_client: TrackingClient,
    ):
        self._job_repo = job_repo
        self._job_service = job_service
        self._dataset_service = dataset_service
        self._tracking_client = tracking_client
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
        job_inference_dict = {
            "name": f"{workflow.name}-inference",
            "model": request.model,
            "dataset": request.dataset,
            "max_samples": request.max_samples,
            "model_url": request.model_url,
            "output_field": request.inference_output_field,
            "system_prompt": request.system_prompt,
            "store_to_dataset": True,
        }
        job_inference_create = JobInferenceCreate.model_validate(job_inference_dict)
        # submit inference job first
        inference_job = JobResponse.model_validate(
            self._job_service.create_job(job_inference_create)
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
        if job_inference_create.store_to_dataset:
            self._job_service._add_dataset_to_db(
                inference_job.id,
                job_inference_create,
                self._dataset_service.s3_filesystem,
            )

        # FIXME The ray status is now _not enough_ to set the job status,
        # since the dataset may still be under creation
        # use the inference job id to recover the dataset record
        dataset_record = self._dataset_service._get_dataset_record_by_job_id(inference_job.id)

        # prepare the inputs for the evaluation job and pass the id of the new dataset
        job_eval_dict = {
            "name": f"{request.name}-evaluation",
            "model": request.model,
            "dataset": dataset_record.id,
            "max_samples": request.max_samples,
            "skip_inference": True,
        }

        # submit the job
        evaluation_job = JobResponse.model_validate(
            self._job_service.create_job(JobEvalLiteCreate.model_validate(job_eval_dict))
        )

        # wait for the evaluation job to complete
        status = await self._job_service.wait_for_job_complete(
            evaluation_job.id, max_wait_time_sec=60 * 10
        )
        if status != JobStatus.SUCCEEDED:
            loguru.logger.error(f"Evaluation job {evaluation_job.id} failed")
            self._tracking_client.update_workflow_status(workflow.id, WorkflowStatus.FAILED)
        try:
            eval_lite_request = JobEvalLiteCreate.model_validate(job_eval_dict)
            loguru.logger.info("Handling evaluation result")

            result_key = str(
                Path(settings.S3_JOB_RESULTS_PREFIX)
                / settings.S3_JOB_RESULTS_FILENAME.format(
                    job_name=eval_lite_request.name, job_id=evaluation_job.id
                )
            )
            with self._dataset_service.s3_filesystem.open(
                f"{settings.S3_BUCKET}/{result_key}", "r"
            ) as f:
                eval_output = EvalJobOutput.model_validate(json.loads(f.read()))

            # TODO this generic interface should probably be the output type of the eval job but
            # we'll make that improvement later
            outputs = RunOutputs(
                metrics={
                    "rouge1_mean": round(eval_output.rouge.rouge1_mean, 3),
                    "rouge2_mean": round(eval_output.rouge.rouge2_mean, 3),
                    "rougeL_mean": round(eval_output.rouge.rougeL_mean, 3),
                    "rougeLsum_mean": round(eval_output.rouge.rougeLsum_mean, 3),
                    "bertscore_f1_mean": round(eval_output.bertscore.f1_mean, 3),
                    "bertscore_precision_mean": round(eval_output.bertscore.precision_mean, 3),
                    "bertscore_recall_mean": round(eval_output.bertscore.recall_mean, 3),
                    "meteor_mean": round(eval_output.meteor.meteor_mean, 3),
                }
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
        return self._tracking_client.get_workflow(workflow_id)

    def create_workflow(
        self, request: WorkflowCreateRequest, background_tasks: BackgroundTasks
    ) -> WorkflowResponse:
        """Creates a new workflow and submits inference and evaluation jobs.

        Args:
            request (WorkflowCreateRequest): The request containing the workflow configuration.
            background_tasks (BackgroundTasks): The background tasks manager for scheduling tasks.

        Returns:
            WorkflowResponse: The response object containing the details of the created workflow.
        """
        loguru.logger.info(
            f"Creating workflow '{request.name}' for experiment ID '{request.experiment_id}'."
        )

        workflow = self._tracking_client.create_workflow(
            experiment_id=request.experiment_id, description=request.description, name=request.name
        )

        # Run the inference and evaluation pipeline as a background task
        background_tasks.add_task(self._run_inference_eval_pipeline, workflow, request)

        return workflow

    # TODO: until we have implemented the association of workflows with experiments,
    #  everything continues to be indexed by experiment_id
    def get_workflow_jobs(self, experiment_id: str) -> ListingResponse[JobResponse]:
        records = self._job_repo.get_by_experiment_id(experiment_id)
        return ListingResponse(
            total=len(records),
            items=[JobResponse.model_validate(x) for x in records],
        )

    def get_workflow_result_download(self, experiment_id: str) -> WorkflowResultDownloadResponse:
        """Return experiment results file URL for downloading."""
        s3 = S3FileSystem()
        # get jobs matching this experiment
        # have a query returning a list of (two) jobs, one inference and one eval,
        # matching the current experiment id. Note that each job has its own type baked in
        # (per https://github.com/mozilla-ai/lumigator/pull/576)
        jobs = self.get_workflow_jobs(experiment_id)

        # iterate on jobs and depending on which job this is, import selected fields
        results = {}

        for job in jobs:
            # Get the dataset from the S3 bucket
            result_key = self._job_service._get_results_s3_key(job.id)
            with s3.open(f"{settings.S3_BUCKET}/{result_key}", "r") as f:
                job_results = json.loads(f.read())

            # we just merge the two dictionaries for now
            results.update(job_results)

        loguru.logger.error(results)

        # Generate presigned download URL for the object
        result_key = self._job_service._get_results_s3_key(experiment_id)
        download_url = self._dataset_service.s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": result_key,
            },
            ExpiresIn=settings.S3_URL_EXPIRATION,
        )

        return WorkflowResultDownloadResponse(id=experiment_id, download_url=download_url)
