import contextlib
import json
from collections.abc import Generator
from datetime import datetime

import boto3
import loguru
from lumigator_schemas.experiments import GetExperimentResponse
from lumigator_schemas.jobs import JobResults
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

    def create_experiment(self, name: str) -> GetExperimentResponse:
        """Create a new experiment."""
        # The name must be unique to all active experiments
        try:
            experiment_id = self._client.create_experiment(name)
        except MlflowException as e:
            # if the experiment name already exists,
            # log a warning and then append a short timestamp to the name
            if "RESOURCE_ALREADY_EXISTS" in str(e):
                print(f"Experiment name '{name}' already exists. Appending timestamp.")
                name = f"{name} {datetime.now().strftime('%Y%m%d%H%M%S')}"
                experiment_id = self._client.create_experiment(name)
            else:
                raise e
        # get the experiment so you can populate the response
        experiment = self._client.get_experiment(experiment_id)
        return GetExperimentResponse(
            id=experiment_id,
            name=name,
            created_at=datetime.fromtimestamp(experiment.creation_time / 1000),
        )

    def delete_experiment(self, experiment_id: str) -> None:
        """Delete an experiment."""
        self._client.delete_experiment(experiment_id)

    def _compile_metrics(self, job_ids: list) -> dict:
        # take the individual metrics from each run and compile them into a single dict
        # for now, assert that each run has no overlapping metrics
        metrics = {}
        for job_id in job_ids:
            run = self._client.get_run(job_id)
            for metric in run.data.metrics:
                assert metric not in metrics
                metrics[metric] = run.data.metrics[metric]

        return metrics

    def _compile_parameters(self, job_ids: list) -> dict:
        # take the individual parameters from each run and compile them into a single dict
        # for now, assert that each run has no overlapping parameters
        parameters = {}
        for job_id in job_ids:
            run = self._client.get_run(job_id)
            for parameter in run.data.params:
                assert parameter not in parameters
                parameters[parameter] = run.data.params[parameter]
        return parameters

    def get_experiment(self, experiment_id: str) -> GetExperimentResponse:
        # get all the runs for the experiment
        experiment = self._client.get_experiment(experiment_id)
        # now get all the workflows associated with that experiment
        all_runs = self._client.search_runs(experiment_ids=[experiment_id])
        # now organize the runs into workflows so that a nested run goes under the parent run
        workflow_ids = []
        for run in all_runs:
            parent_id = run.data.tags.get(MLFLOW_PARENT_RUN_ID)
            # if it has a parent id then it's a run, if not then it's a workflow
            if parent_id is None:
                workflow_ids.append(run.info.run_id)
        workflows = [self.get_workflow(workflow_id) for workflow_id in workflow_ids]
        return GetExperimentResponse(
            id=experiment_id,
            name=experiment.name,
            created_at=datetime.fromtimestamp(experiment.creation_time / 1000),
            workflows=workflows,
        )

    def update_experiment(self, experiment_id: str, new_name: str) -> None:
        raise NotImplementedError

    def list_experiments(self, skip: int, limit: int) -> list:
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
            if not response:
                break
            page_token = response[-1].experiment_id

        return experiments[:limit] if limit is not None else experiments

    def experiments_count(self):
        return len(self.list_experiments(skip=0, limit=None))

    # this corresponds to creating a run in MLflow.
    # The run will have n number of nested runs,
    # which correspond to what we call "jobs" in our system
    def create_workflow(self, experiment_id: str, description: str, name: str) -> WorkflowResponse:
        """Create a new workflow."""
        # make sure its status is CREATED
        workflow = self._client.create_run(
            experiment_id=experiment_id,
            tags={
                "mlflow.runName": name,
                "status": WorkflowStatus.CREATED,
                "description": description,
            },
        )
        return WorkflowResponse(
            id=workflow.info.run_id,
            experiment_id=experiment_id,
            name=name,
            description=description,
            status=workflow.data.tags.get("status"),
            created_at=datetime.fromtimestamp(workflow.info.start_time / 1000),
        )

    def get_workflow(self, workflow_id: str) -> WorkflowDetailsResponse:
        # get the workflow, and for each job associated with with workflow, get its status
        workflow = self._client.get_run(workflow_id)
        # similar to the get_experiment method, but for a single workflow,
        # we need to get all the runs
        # search for all runs that have the tag "mlflow.parentRunId" equal to the workflow_id
        all_jobs = self._client.search_runs(
            experiment_ids=[workflow.info.experiment_id],
            filter_string=f"tags.{MLFLOW_PARENT_RUN_ID} = '{workflow_id}'",
        )
        all_job_ids = [run.info.run_id for run in all_jobs]

        workflow_details = WorkflowDetailsResponse(
            id=workflow_id,
            experiment_id=workflow.info.experiment_id,
            description=workflow.data.tags.get("description"),
            name=workflow.data.tags.get("mlflow.runName"),
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
        compiled_results = {}
        s3 = S3FileSystem()
        for job in workflow_details.jobs:
            # look for all parameter keys that end in "_s3_path" and download the file
            for param in job.parameters:
                if param["name"].endswith("_s3_path"):
                    # download the file
                    # get the file from the S3 bucket
                    with s3.open(f"{param['value']}") as f:
                        job_results = json.loads(f.read())
                    # if any keys are the same, log a warning and then overwrite the key
                    for key in job_results.keys():
                        if key in compiled_results:
                            loguru.logger.warning(
                                f"Key '{key}' already exists in the compiled results. Overwriting."
                            )
                    # merge the results into the compiled results
                    compiled_results.update(job_results)
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
        self._client.set_tag(workflow_id, "status", status)

    def delete_workflow(self, workflow_id: str) -> None:
        raise NotImplementedError

    def list_workflows(self, experiment_id: str) -> list:
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

    def update_job(self, job_id: str, new_data: dict):
        raise NotImplementedError

    def get_job(self, job_id: str):
        # look up the job and return it as a JobResult
        run = self._client.get_run(job_id)
        return JobResults(
            id=job_id,
            metrics=[
                {"name": metric[0], "value": metric[1]} for metric in run.data.metrics.items()
            ],
            parameters=[{"name": param[0], "value": param[1]} for param in run.data.params.items()],
            metric_url="TODO",
            artifact_url="TODO",
        )

    def delete_job(self, job_id: str):
        raise NotImplementedError

    def list_jobs(self, experiment_id: str, workflow_id: str):
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
