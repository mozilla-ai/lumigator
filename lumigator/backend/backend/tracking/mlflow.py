import contextlib
import http
import json
from collections import defaultdict
from collections.abc import Generator
from datetime import datetime
from http import HTTPStatus
from urllib.parse import urljoin
from uuid import UUID

import loguru
import requests
from lumigator_schemas.experiments import GetExperimentResponse
from lumigator_schemas.jobs import JobLogsResponse, JobResultObject, JobResults
from lumigator_schemas.tasks import TaskDefinition
from lumigator_schemas.utils.model_operations import merge_models
from lumigator_schemas.workflows import WorkflowDetailsResponse, WorkflowResponse, WorkflowStatus
from mlflow.entities import Experiment as MlflowExperiment
from mlflow.entities import Run as MlflowRun
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient
from mlflow.utils.mlflow_tags import MLFLOW_PARENT_RUN_ID
from mypy_boto3_s3.client import S3Client
from pydantic import TypeAdapter
from s3fs import S3FileSystem

from backend.services.exceptions.job_exceptions import JobNotFoundError, JobUpstreamError
from backend.settings import settings
from backend.tracking.schemas import RunOutputs
from backend.tracking.tracking_interface import TrackingClient


class MLflowTrackingClient(TrackingClient):
    """MLflow implementation of the TrackingClient interface."""

    def __init__(self, tracking_uri: str, s3_file_system: S3FileSystem, s3_client: S3Client):
        self._client = MlflowClient(tracking_uri=tracking_uri)
        self._s3_file_system = s3_file_system
        self._s3_client = s3_client

    def create_experiment(
        self,
        name: str,
        description: str,
        task_definition: TaskDefinition,
        dataset: UUID,
        max_samples: int,
    ) -> GetExperimentResponse:
        """Create a new experiment."""
        # The name must be unique to all active experiments
        # Refactor like "for key in [...] set tag ..."
        try:
            experiment_id = self._client.create_experiment(name)
            self._client.set_experiment_tag(experiment_id, "description", description)
            self._client.set_experiment_tag(experiment_id, "task_definition", task_definition.model_dump_json())
            self._client.set_experiment_tag(experiment_id, "dataset", dataset)
            self._client.set_experiment_tag(experiment_id, "max_samples", str(max_samples))
            self._client.set_experiment_tag(experiment_id, "lumigator_version", "0.2.1")
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
                self._client.set_experiment_tag(experiment_id, "task_definition", task_definition.model_dump_json())
                self._client.set_experiment_tag(experiment_id, "dataset", dataset)
                self._client.set_experiment_tag(experiment_id, "max_samples", str(max_samples))
                self._client.set_experiment_tag(experiment_id, "lumigator_version", "0.2.1")
            else:
                raise e
        # get the experiment so you can populate the response
        experiment = self._client.get_experiment(experiment_id)
        return GetExperimentResponse(
            id=experiment_id,
            description=description,
            task_definition=task_definition,
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

    def get_experiment(self, experiment_id: str) -> GetExperimentResponse | None:
        """Get an experiment and all its workflows."""
        try:
            experiment = self._client.get_experiment(experiment_id)
        except MlflowException as e:
            if e.get_http_status_code() == http.HTTPStatus.NOT_FOUND:
                return None
            raise e

        # If the experiment is in the deleted lifecylce, return None
        if experiment.lifecycle_stage == "deleted":
            return None
        return self._format_experiment(experiment)

    def _format_experiment(self, experiment: MlflowExperiment) -> GetExperimentResponse:
        # now get all the workflows associated with that experiment
        workflow_ids = self._find_workflows(experiment.experiment_id)
        workflows = [
            workflow
            for workflow in (self.get_workflow(workflow_id) for workflow_id in workflow_ids)
            if workflow is not None
        ]
        task_definition_json = experiment.tags.get("task_definition")
        task_definition = TypeAdapter(TaskDefinition).validate_python(json.loads(task_definition_json))
        return GetExperimentResponse(
            id=experiment.experiment_id,
            name=experiment.name,
            description=experiment.tags.get("description") or "",
            task_definition=task_definition,
            dataset=experiment.tags.get("dataset") or "",
            max_samples=int(experiment.tags.get("max_samples") or "-1"),
            created_at=datetime.fromtimestamp(experiment.creation_time / 1000),
            updated_at=datetime.fromtimestamp(experiment.last_update_time / 1000),
            workflows=workflows,
        )

    def update_experiment(self, experiment_id: str, new_name: str) -> None:
        """Update the name of an experiment."""
        raise NotImplementedError

    def list_experiments(self, skip: int, limit: int | None) -> list[GetExperimentResponse]:
        """List all experiments."""
        page_token = None
        experiments = []
        skipped = 0
        while True:
            response = self._client.search_experiments(
                page_token=page_token, filter_string='tags.lumigator_version != ""'
            )
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
        return [self._format_experiment(experiment) for experiment in reduced_experiments]

    # TODO find a cheaper call
    def experiments_count(self):
        """Get the number of experiments."""
        return len(self.list_experiments(skip=0, limit=None))

    # this corresponds to creating a run in MLflow.
    # The run will have n number of nested runs,
    # which correspond to what we call "jobs" in our system
    def create_workflow(
        self, experiment_id: str, description: str, name: str, model: str, system_prompt: str
    ) -> WorkflowResponse:
        """Create a new workflow."""
        # make sure its status is CREATED
        workflow = self._client.create_run(
            experiment_id=experiment_id,
            tags={
                "mlflow.runName": name,
                "status": WorkflowStatus.CREATED.value,
                "description": description,
                "model": model,
                "system_prompt": system_prompt,
            },
        )
        return WorkflowResponse(
            id=workflow.info.run_id,
            experiment_id=experiment_id,
            name=name,
            model=model,
            description=description,
            system_prompt=system_prompt,
            status=WorkflowStatus.CREATED,
            created_at=datetime.fromtimestamp(workflow.info.start_time / 1000),
        )

    def get_workflow(self, workflow_id: str) -> WorkflowDetailsResponse | None:
        """Retrieve a workflow and its associated jobs."""
        workflow = self._fetch_workflow_run(workflow_id)
        if not workflow:
            return None

        jobs = self._get_job_ids(workflow_id, workflow.info.experiment_id)
        workflow_details = self._build_workflow_response(workflow, jobs)

        if workflow_details.status == WorkflowStatus.SUCCEEDED:
            # Only compile the result JSON artifact of all the jobs, if the workflow has succeeded.
            self._generate_compiled_results(workflow_id, workflow_details.jobs)
            # Update the download URL in the response now that the compiled results are available.
            workflow_details.artifacts_download_url = self._generate_presigned_url(workflow_id)

        return workflow_details

    def update_workflow_status(self, workflow_id: str, status: WorkflowStatus) -> None:
        """Update the status of a workflow."""
        self._client.set_tag(workflow_id, "status", status.value)

    def get_workflow_logs(self, workflow_id: str) -> JobLogsResponse:
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
            system_prompt=workflow.data.tags.get("system_prompt"),
            status=WorkflowStatus(workflow.data.tags.get("status")),
            created_at=datetime.fromtimestamp(workflow.info.start_time / 1000),
        )

    def list_workflows(self, experiment_id: str) -> list:
        """List all workflows in an experiment."""
        raise NotImplementedError

    def create_job(self, experiment_id: str, workflow_id: str, name: str, job_id: str) -> str:
        """Link a started job to an experiment and a workflow."""
        run = self._client.create_run(
            experiment_id=experiment_id,
            tags={MLFLOW_PARENT_RUN_ID: workflow_id, "mlflow.runName": name},
        )
        # log the ray_job_id as a param, we'll use this to get the logs later
        self._client.log_param(run.info.run_id, "ray_job_id", job_id)
        return run.info.run_id

    def update_job(self, job_id: str, data: RunOutputs):
        """Update the metrics and parameters of a job."""
        for metric, value in data.metrics.items():
            self._client.log_metric(job_id, metric, value)
        for parameter, value in data.parameters.items():
            self._client.log_param(job_id, parameter, value)

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

    def list_jobs(self, workflow_id: str):
        """List all jobs in a workflow."""
        workflow_run = self._client.get_run(workflow_id)
        # get the jobs associated with the workflow
        all_jobs = self._client.search_runs(
            experiment_ids=[workflow_run.info.experiment_id],
            filter_string=f"tags.{MLFLOW_PARENT_RUN_ID} = '{workflow_id}'",
        )
        return all_jobs

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

    def _get_ray_job_logs(self, ray_job_id: str):
        """Get the logs for a Ray job."""
        resp = requests.get(urljoin(settings.RAY_JOBS_URL, f"{ray_job_id}/logs"), timeout=5)  # 5 sec

        if resp.status_code == HTTPStatus.NOT_FOUND:
            loguru.logger.error(f"Upstream job logs not found: {resp.status_code}, error: {resp.text or ''}")
            raise JobNotFoundError(UUID(ray_job_id), "Ray job logs not found") from None
        elif resp.status_code != HTTPStatus.OK:
            loguru.logger.error(
                f"Unexpected status code getting job logs: {resp.status_code}, \
                    error: {resp.text or ''}"
            )
            raise JobUpstreamError(ray_job_id, "Non OK status code retrieving Ray job information") from None

        try:
            metadata = json.loads(resp.text)
            return JobLogsResponse(**metadata)
        except json.JSONDecodeError as e:
            loguru.logger.error(f"JSON decode error: {e}")
            loguru.logger.error(f"Response text: {resp.text}")
            raise JobUpstreamError(ray_job_id, "JSON decode error in Ray response") from e

    def _generate_presigned_url(self, workflow_id: str) -> str:
        """Generate a pre-signed URL for the compiled artifact."""
        return self._s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET, "Key": self._get_s3_path(workflow_id, "compiled.json")},
            ExpiresIn=settings.S3_URL_EXPIRATION,
        )

    def _upload_to_s3(self, s3_path: str, data):
        """Upload compiled results to S3."""
        with self._s3_file_system.open(s3_path, "w") as f:
            f.write(json.dumps(data))

    def _build_workflow_response(self, workflow: MlflowRun, job_ids: list) -> WorkflowDetailsResponse:
        """Construct a WorkflowDetailsResponse object ignoring the `artifacts_download_url`."""
        return WorkflowDetailsResponse(
            id=workflow.info.run_id,
            experiment_id=workflow.info.experiment_id,
            description=workflow.data.tags.get("description"),
            name=workflow.data.tags.get("mlflow.runName"),
            model=workflow.data.tags.get("model"),
            system_prompt=workflow.data.tags.get("system_prompt"),
            status=WorkflowStatus(workflow.data.tags.get("status")),
            created_at=datetime.fromtimestamp(workflow.info.start_time / 1000),
            jobs=[self.get_job(job_id) for job_id in job_ids],
            metrics=self._compile_metrics(job_ids),
            parameters=self._compile_parameters(job_ids),
        )

    def _generate_compiled_results(self, workflow_id: str, jobs: list[JobResults]) -> None:
        """Generates a single compiled JSON artifact of aggregated job results belonging to the workflow.

        Data is compiled in a last-write-wins scenario when there are matching keys with different values.

        :param workflow_id: The ID of the workflow.
        :param jobs: A list of jobs to try to retrieve result data for to aggregate.
        """
        # Nothing to do if there are no jobs for this workflow.
        if not jobs:
            return

        # Don't recompile if the artifact already exists.
        workflow_s3_path = self._get_s3_path(workflow_id, "compiled.json")
        if self._s3_file_system.exists(workflow_s3_path):
            return

        aggregated_results = JobResultObject()
        for job in jobs:
            # If no valid s3_path_value is found, skip this job.
            if not (
                job_s3_path := next(
                    (
                        param.get("value")
                        for param in job.parameters or []
                        if param.get("name", "").endswith("_s3_path")
                    ),
                    None,
                )
            ):
                continue

            with self._s3_file_system.open(job_s3_path) as f:
                job_results = JobResultObject.model_validate(json.loads(f.read()))

            aggregated_results, overwritten_keys, skipped_keys = merge_models(aggregated_results, job_results)

            # Make note of the keys that were overwritten, and skipped when merging this job's results.
            self._log_merged_keys(workflow_id, job.id, overwritten_keys, skipped_keys)

        # Upload the compiled results to S3.
        self._upload_to_s3(workflow_s3_path, aggregated_results.model_dump())

    def _group_keys_by_top_level(self, keys: set[str]) -> dict[str, list[str]]:
        """Groups a set of keys (formatted with dotted notation) by their top-level category.

        This function splits each key at the first dot ('.') to separate the top-level category
        from any sub-keys. If a key doesn't contain a dot, it is treated as a top-level key with
        no sub-keys. The result is a dictionary where the keys are the top-level categories and
        the values are lists of associated sub-keys, sorted alphabetically.

        :param keys: A set of keys formatted in dotted notation, where each key may consist of
                      a top-level category followed by one or more sub-keys.
        :return: A dictionary mapping top-level categories to lists of their associated sub-keys,
                 sorted alphabetically by the sub-keys.
        """
        accumulated = defaultdict(list)

        for key in keys:
            if "." in key:
                top_level_key, subkey = key.split(".", 1)
                accumulated[top_level_key].append(subkey)
            else:
                # If there's no dot, treat it as a top-level key without sub-keys
                accumulated[key].append("")

        return {key: sorted(values) for key, values in sorted(accumulated.items())}

    def _log_merged_keys(self, workflow_id: str, job_id: str, overwritten_keys: set[str], skipped_keys: set[str]):
        """Logs skipped and overwritten keys during the merge process.

        :param workflow_id: The ID of the workflow.
        :param job_id: The ID of the job.
        :param overwritten_keys: A set of keys (to be logged at WARNING level) that were
                overwritten during the merge process.
        :param skipped_keys: A set of keys (to be logged at DEBUG level) that were
                skipped during the merge process
        """
        if overwritten_keys:
            loguru.logger.opt(lazy=True).warning(
                "Workflow: '{}'. Job '{}'. Overwritten existing keys: {}",
                lambda: workflow_id,
                lambda: job_id,
                lambda: ", ".join(
                    f"{key} [{', '.join(f'.{sub}' for sub in sub_keys) if any(sub_keys) else ''}]"
                    if any(sub_keys)
                    else key
                    for key, sub_keys in (lambda d: d.items())(self._group_keys_by_top_level(overwritten_keys))
                ),
            )

        if skipped_keys:
            loguru.logger.opt(lazy=True).debug(
                "Workflow: '{}'. Job '{}'. Skipped keys: {}",
                lambda: workflow_id,
                lambda: job_id,
                lambda: ", ".join(
                    f"{key} [{', '.join(f'.{sub}' for sub in sub_keys) if any(sub_keys) else ''}]"
                    if any(sub_keys)
                    else key
                    for key, sub_keys in (lambda d: d.items())(self._group_keys_by_top_level(skipped_keys))
                ),
            )

    def _fetch_workflow_run(self, workflow_id: str):
        """Try to fetch a workflow run from MLFlow.

        :param workflow_id: The ID of the workflow to fetch.
        :return: The workflow run if it exists and is not deleted, otherwise None.
        :raises MlflowException: If an unexpected error occurs.
        """
        try:
            workflow = self._client.get_run(workflow_id)
        except MlflowException as e:
            if e.get_http_status_code() == http.HTTPStatus.NOT_FOUND:
                return None
            raise e

        return None if workflow.info.lifecycle_stage == "deleted" else workflow

    def _get_job_ids(self, workflow_id: str, experiment_id: str) -> list:
        """Get the IDs of all jobs associated with a workflow.

        :param workflow_id: The ID of the workflow.
        :param experiment_id: The ID of the experiment tied to this workflow.
        :return: A list of job IDs.
        """
        all_jobs = self._client.search_runs(
            experiment_ids=[experiment_id],
            filter_string=f"tags.{MLFLOW_PARENT_RUN_ID} = '{workflow_id}'",
            order_by=["start_time DESC"],
        )
        return [job.info.run_id for job in all_jobs]

    def _get_s3_path(self, workflow_id: str, filename: str) -> str:
        """Construct an S3 path for workflow artifacts."""
        return f"{settings.S3_BUCKET}/workflows/results/{workflow_id}/{filename}"


class MLflowClientManager:
    """Connection manager for MLflow client."""

    def __init__(self, tracking_uri: str, s3_file_system: S3FileSystem, s3_client: S3Client):
        self._tracking_uri = tracking_uri
        self._s3_file_system = s3_file_system
        self._s3_client = s3_client

    @contextlib.contextmanager
    def connect(self) -> Generator[TrackingClient, None, None]:
        """Yield an MLflow client, handling exceptions."""
        tracking_client = MLflowTrackingClient(
            tracking_uri=self._tracking_uri,
            s3_file_system=self._s3_file_system,
            s3_client=self._s3_client,
        )
        try:
            yield tracking_client
        except MlflowException as e:
            print(f"MLflowException occurred: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise
