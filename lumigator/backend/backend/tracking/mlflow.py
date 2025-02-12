import contextlib
import json
from collections.abc import Generator
from datetime import datetime
from http import HTTPStatus
from urllib.parse import urljoin
from uuid import UUID

import boto3
import loguru
import requests
from fastapi import HTTPException
from lumigator_schemas.experiments import GetExperimentResponse
from lumigator_schemas.jobs import JobLogsResponse, JobResultObject, JobResults
from lumigator_schemas.workflows import WorkflowDetailsResponse, WorkflowResponse, WorkflowStatus
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient
from mlflow.utils.mlflow_tags import MLFLOW_PARENT_RUN_ID
from s3fs import S3FileSystem

from backend.settings import settings
from backend.tracking.schemas import RunOutputs
from backend.tracking.tracking_interface import TrackingClient, TrackingClientManager


class MLflowTrackingClient(TrackingClient):
    """MLflow implementation of the TrackingClient interface."""

    def __init__(self, tracking_uri: str):
        self._client = MlflowClient(tracking_uri=tracking_uri)

    def create_experiment(
        self, name: str, description: str, task: str, dataset: UUID, max_samples: int
    ) -> GetExperimentResponse:
        """Create a new experiment."""
        # The name must be unique to all active experiments
        # Refactor like "for key in [...] set tag ..."
        try:
            experiment_id = self._client.create_experiment(name)
            self._client.set_experiment_tag(experiment_id, "description", description)
            self._client.set_experiment_tag(experiment_id, "task", task)
            self._client.set_experiment_tag(experiment_id, "dataset", dataset)
            loguru.logger.critical(f"Storing max_samples: {str(max_samples)}")
            self._client.set_experiment_tag(experiment_id, "max_samples", str(max_samples))
        # FIXME Let the user decide in the case of failures.
        # Also, use a uuid as name and an arbitrary tag as descriptive name
        except MlflowException as e:
            # if the experiment name already exists,
            # log a warning and then append a short timestamp to the name
            if "RESOURCE_ALREADY_EXISTS" in str(e):
                print(f"Experiment name '{name}' already exists. Appending timestamp.")
                name = f"{name} {datetime.now().strftime('%Y%m%d%H%M%S')}"
                experiment_id = self._client.create_experiment(name)
                self._client.set_experiment_tag(experiment_id, "description", description)
                self._client.set_experiment_tag(experiment_id, "task", task)
                self._client.set_experiment_tag(experiment_id, "dataset", dataset)
                loguru.logger.critical(f"Storing max_samples: {str(max_samples)}")
                self._client.set_experiment_tag(experiment_id, "max_samples", str(max_samples))
            else:
                raise e
        # get the experiment so you can populate the response
        experiment = self._client.get_experiment(experiment_id)
        return GetExperimentResponse(
            id=experiment_id,
            description=description,
            task=task,
            name=name,
            dataset=dataset,
            max_samples=max_samples,
            created_at=datetime.fromtimestamp(experiment.creation_time / 1000),
        )

    def delete_experiment(self, experiment_id: str) -> None:
        """Delete an experiment. Although Mflow has a delete_experiment method,
        We will use the functions of this class instead, so that we make sure we correctly
        clean up all the artifacts/runs/etc. associated with the experiment.
        """
        workflow_ids = self._find_workflows(experiment_id)
        # delete all the workflows
        for workflow_id in workflow_ids:
            self.delete_workflow(workflow_id)
        # delete the experiment
        self._client.delete_experiment(experiment_id)

    def _compile_metrics(self, job_ids: list) -> dict:
        """Take the individual metrics from each run and compile them into a single dict
        for now, assert that each run has no overlapping metrics
        """
        metrics = {}
        for job_id in job_ids:
            run = self._client.get_run(job_id)
            for metric in run.data.metrics:
                assert metric not in metrics
                metrics[metric] = run.data.metrics[metric]

        return metrics

    def _compile_parameters(self, job_ids: list) -> dict:
        """Take the individual parameters from each run and compile them into a single dict
        for now, assert that each run has no overlapping parameters
        """
        parameters = {}
        for job_id in job_ids:
            run = self._client.get_run(job_id)
            for parameter in run.data.params:
                # if the parameter shows up in multiple runs, prepend the run_name to the key
                # TODO: this is a hacky way to handle this,
                #  we should come up with a better solution but at least it keeps the info
                if parameter in parameters:
                    parameters[f"{run.data.tags['mlflow.runName']}_{parameter}"] = run.data.params[parameter]
                parameters[parameter] = run.data.params[parameter]
        return parameters

    def _find_workflows(self, experiment_id: str) -> list:
        """Find all the workflows associated with an experiment."""
        all_runs = self._client.search_runs(experiment_ids=[experiment_id])
        # now organize the runs into workflows so that a nested run goes under the parent run
        workflow_ids = []
        for run in all_runs:
            parent_id = run.data.tags.get(MLFLOW_PARENT_RUN_ID)
            # if it has a parent id then it's a run, if not then it's a workflow
            if parent_id is None:
                workflow_ids.append(run.info.run_id)
        return workflow_ids

    def get_experiment(self, experiment_id: str):
        """Get an experiment and all its workflows."""
        experiment = self._client.get_experiment(experiment_id)
        # If the experiment is in the deleted lifecylce, return None
        if experiment.lifecycle_stage == "deleted":
            return None

        # now get all the workflows associated with that experiment
        workflow_ids = self._find_workflows(experiment_id)
        workflows = [self.get_workflow(workflow_id) for workflow_id in workflow_ids]
        max_samples = int(experiment.tags.get("max_samples"))
        loguru.logger.critical(f"Retrieving max_samples: {max_samples}")
        return GetExperimentResponse(
            id=experiment_id,
            name=experiment.name,
            description=experiment.tags.get("description") or "",
            task=experiment.tags.get("task") or "",
            dataset=experiment.tags.get("dataset") or "",
            max_samples=max_samples,
            created_at=datetime.fromtimestamp(experiment.creation_time / 1000),
            updated_at=datetime.fromtimestamp(experiment.last_update_time / 1000),
            workflows=workflows,
        )

    def update_experiment(self, experiment_id: str, new_name: str) -> None:
        """Update the name of an experiment."""
        raise NotImplementedError

    def list_experiments(self, skip: int, limit: int) -> list[GetExperimentResponse]:
        """List all experiments."""
        page_token = None
        experiments = []
        skipped = 0
        while True:
            response = self._client.search_experiments(page_token=page_token)
            if skipped < skip:
                skipped += len(response)
                if skipped > skip:
                    response = response[skip - (skipped - len(response)) :]
                else:
                    continue
            experiments.extend(response)
            if limit is not None and len(experiments) >= limit:
                break
            if response.token is None:
                break
        reduced_experiments = experiments[:limit] if limit is not None else experiments
        return [
            GetExperimentResponse(
                id=experiment.experiment_id,
                name=experiment.name,
                description=experiment.tags.get("description") or "",
                created_at=datetime.fromtimestamp(experiment.creation_time / 1000),
                updated_at=datetime.fromtimestamp(experiment.last_update_time / 1000),
            )
            for experiment in reduced_experiments
        ]

    def experiments_count(self):
        """Get the number of experiments."""
        return len(self.list_experiments(skip=0, limit=None))

    # this corresponds to creating a run in MLflow.
    # The run will have n number of nested runs,
    # which correspond to what we call "jobs" in our system
    def create_workflow(self, experiment_id: str, description: str, name: str, model: str) -> WorkflowResponse:
        """Create a new workflow."""
        # make sure its status is CREATED
        workflow = self._client.create_run(
            experiment_id=experiment_id,
            tags={
                "mlflow.runName": name,
                "status": WorkflowStatus.CREATED,
                "description": description,
                "model": model,
            },
        )
        return WorkflowResponse(
            id=workflow.info.run_id,
            experiment_id=experiment_id,
            name=name,
            model=model,
            description=description,
            status=WorkflowStatus.CREATED,
            created_at=datetime.fromtimestamp(workflow.info.start_time / 1000),
        )

    def get_workflow(self, workflow_id: str) -> WorkflowDetailsResponse:
        """Get a workflow and all its jobs."""
        workflow = self._client.get_run(workflow_id)
        if workflow.info.lifecycle_stage == "deleted":
            return None
        # similar to the get_experiment method, but for a single workflow,
        # we need to get all the runs
        # search for all runs that have the tag "mlflow.parentRunId" equal to the workflow_id
        all_jobs = self._client.search_runs(
            experiment_ids=[workflow.info.experiment_id],
            filter_string=f"tags.{MLFLOW_PARENT_RUN_ID} = '{workflow_id}'",
        )
        all_job_ids = [run.info.run_id for run in all_jobs]
        # sort the jobs by created_at, with the oldest last
        all_jobs = sorted(all_jobs, key=lambda x: x.info.start_time)

        workflow_details = WorkflowDetailsResponse(
            id=workflow_id,
            experiment_id=workflow.info.experiment_id,
            description=workflow.data.tags.get("description"),
            name=workflow.data.tags.get("mlflow.runName"),
            model=workflow.data.tags.get("model"),
            status=WorkflowStatus(WorkflowStatus[workflow.data.tags.get("status").split(".")[1]]),
            created_at=datetime.fromtimestamp(workflow.info.start_time / 1000),
            jobs=[self.get_job(job_id) for job_id in all_job_ids],
            metrics=self._compile_metrics(all_job_ids),
            parameters=self._compile_parameters(all_job_ids),
        )
        # Currently, only compile the result json artifact if the workflow has succeeded
        if workflow_details.status != WorkflowStatus.SUCCEEDED:
            return workflow_details
        # now we need to combine all of the files that were output into a single json.
        # look through every job associated with this workflow and get the results
        # combine them into a single json file, put that back into s3, and then generate
        # a presigned URL for that file
        # check if the compiled results already exist
        s3 = S3FileSystem()
        if not s3.exists(f"{settings.S3_BUCKET}/{workflow_id}/compiled.json"):
            compiled_results = {"metrics": {}, "parameters": {}, "artifacts": {}}
            for job in workflow_details.jobs:
                # look for all parameter keys that end in "_s3_path" and download the file
                for param in job.parameters:
                    if param["name"].endswith("_s3_path"):
                        # download the file
                        # get the file from the S3 bucket
                        with s3.open(f"{param['value']}") as f:
                            job_results = JobResultObject.model_validate(json.loads(f.read()))
                        # if any keys are the same, log a warning and then overwrite the key
                        for job_result_item in job_results:
                            if job_result_item[1] is None:
                                loguru.logger.info(f"No {job_result_item[0]} found for job {job.id}.")
                                continue
                            for key in job_result_item[1].keys():
                                if key in compiled_results[job_result_item[0]]:
                                    loguru.logger.warning(f"Key '{key}' already exists in the results. Overwriting.")
                                # merge the results into the compiled results
                                compiled_results[job_result_item[0]][key] = job_result_item[1][key]
            with s3.open(f"{settings.S3_BUCKET}/{workflow_id}/compiled.json", "w") as f:
                f.write(json.dumps(compiled_results))
            # Generate presigned download URL for the object
        s3_client = boto3.client("s3", endpoint_url=settings.S3_ENDPOINT_URL)
        download_url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": f"{workflow_id}/compiled.json",
            },
            ExpiresIn=settings.S3_URL_EXPIRATION,
        )
        workflow_details.artifacts_download_url = download_url
        return workflow_details

    def update_workflow_status(self, workflow_id: str, status: WorkflowStatus) -> None:
        """Update the status of a workflow."""
        self._client.set_tag(workflow_id, "status", status)

    def _get_ray_job_logs(self, ray_job_id: str):
        """Get the logs for a Ray job."""
        resp = requests.get(urljoin(settings.RAY_JOBS_URL, f"{ray_job_id}/logs"), timeout=5)  # 5 sec

        if resp.status_code == HTTPStatus.NOT_FOUND:
            loguru.logger.error(f"Upstream job logs not found: {resp.status_code}, error: {resp.text or ''}")
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Job logs for ID: {ray_job_id} not found",
            )
        elif resp.status_code != HTTPStatus.OK:
            loguru.logger.error(
                f"Unexpected status code getting job logs: {resp.status_code}, \
                    error: {resp.text or ''}"
            )
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error getting job logs for ID: {ray_job_id}",
            )

        try:
            metadata = json.loads(resp.text)
            return JobLogsResponse(**metadata)
        except json.JSONDecodeError as e:
            loguru.logger.error(f"JSON decode error: {e}")
            loguru.logger.error(f"Response text: {resp.text}")
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Invalid JSON response") from e

    def get_workflow_logs(self, workflow_id: str) -> JobLogsResponse:
        """Get the logs for a workflow."""
        workflow_run = self._client.get_run(workflow_id)
        # get the jobs associated with the workflow
        all_jobs = self._client.search_runs(
            experiment_ids=[workflow_run.info.experiment_id],
            filter_string=f"tags.{MLFLOW_PARENT_RUN_ID} = '{workflow_id}'",
        )
        # sort the jobs by created_at, with the oldest last
        all_jobs = sorted(all_jobs, key=lambda x: x.info.start_time)
        all_ray_job_ids = [run.data.params.get("ray_job_id") for run in all_jobs]
        logs = [self._get_ray_job_logs(ray_job_id) for ray_job_id in all_ray_job_ids]
        # combine the logs into a single string
        # TODO: This is not a great solution but it matches the current API
        return JobLogsResponse(logs="\n================\n".join([log.logs for log in logs]))

    def delete_workflow(self, workflow_id: str) -> WorkflowResponse:
        """Delete a workflow."""
        # first, get the workflow
        workflow = self._client.get_run(workflow_id)
        # get all the jobs associated with the workflow
        all_jobs = self._client.search_runs(
            experiment_ids=[workflow.info.experiment_id],
            filter_string=f"tags.{MLFLOW_PARENT_RUN_ID} = '{workflow_id}'",
        )
        all_job_ids = [run.info.run_id for run in all_jobs]
        # delete all the jobs
        for job_id in all_job_ids:
            self.delete_job(job_id)
        # delete the workflow
        self._client.delete_run(workflow_id)
        # TODO: delete the compiled results from S3, and any saved artifacts
        return WorkflowResponse(
            id=workflow_id,
            experiment_id=workflow.info.experiment_id,
            name=workflow.data.tags.get("mlflow.runName"),
            description=workflow.data.tags.get("description"),
            model=workflow.data.tags.get("model"),
            status=WorkflowStatus(WorkflowStatus[workflow.data.tags.get("status").split(".")[1]]),
            created_at=datetime.fromtimestamp(workflow.info.start_time / 1000),
        )

    def list_workflows(self, experiment_id: str) -> list:
        """List all workflows in an experiment."""
        raise NotImplementedError

    def create_job(self, experiment_id: str, workflow_id: str, name: str, data: RunOutputs):
        """Log the run output to MLflow."""
        run = self._client.create_run(
            experiment_id=experiment_id,
            tags={MLFLOW_PARENT_RUN_ID: workflow_id, "mlflow.runName": name},
        )
        for metric, value in data.metrics.items():
            self._client.log_metric(run.info.run_id, metric, value)
        for parameter, value in data.parameters.items():
            self._client.log_param(run.info.run_id, parameter, value)

        # log the ray_job_id as a param, we'll use this to get the logs later
        self._client.log_param(run.info.run_id, "ray_job_id", data.ray_job_id)

    def update_job(self, job_id: str, new_data: dict):
        """Update the metrics and parameters of a job."""
        raise NotImplementedError

    def get_job(self, job_id: str):
        """Get the results of a job."""
        run = self._client.get_run(job_id)
        if run.info.lifecycle_stage == "deleted":
            return None
        return JobResults(
            id=job_id,
            metrics=[{"name": metric[0], "value": metric[1]} for metric in run.data.metrics.items()],
            parameters=[{"name": param[0], "value": param[1]} for param in run.data.params.items()],
            metric_url="TODO",
            artifact_url="TODO",
        )

    def delete_job(self, job_id: str):
        """Delete a job."""
        self._client.delete_run(job_id)

    def list_jobs(self, experiment_id: str, workflow_id: str):
        """List all jobs in a workflow."""
        raise NotImplementedError


class MLflowClientManager(TrackingClientManager):
    """Connection manager for MLflow client."""

    @contextlib.contextmanager
    def connect(self) -> Generator[MLflowTrackingClient, None, None]:
        """Yield an MLflow client, handling exceptions."""
        tracking_client = MLflowTrackingClient(tracking_uri=self._tracking_uri)
        try:
            yield tracking_client
        except MlflowException as e:
            print(f"MLflowException occurred: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise
