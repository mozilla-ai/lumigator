import contextlib
from collections.abc import Generator

from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient
from mlflow.utils.mlflow_tags import MLFLOW_PARENT_RUN_ID

from backend.tracking.tracking_interface import TrackingClient, TrackingClientManager


class MLflowTrackingClient(TrackingClient):
    """MLflow implementation of the TrackingClient interface."""

    def __init__(self, tracking_uri: str):
        self._client = MlflowClient(tracking_uri=tracking_uri)

    def create_experiment(self, name: str) -> str:
        """Create a new experiment."""
        # The name must be unique to all active experiments
        return self._client.create_experiment(name)

    def delete_experiment(self, experiment_id: str) -> None:
        """Delete an experiment."""
        self._client.delete_experiment(experiment_id)

    # this corresponds to creating a run in MLflow.
    # The run will have n number of nested runs,
    # which correspond to what we call "jobs" in our system
    def create_workflow(self, experiment_id: str) -> str:
        """Create a new workflow."""
        workflow = self._client.create_run(experiment_id=experiment_id)
        return workflow.info.run_id

    def create_job(self, experiment_id: str, workflow_id: str, data: dict):
        """Log the run output to MLflow."""
        _ = self._client.create_run(
            experiment_id=experiment_id, tags={MLFLOW_PARENT_RUN_ID: workflow_id}
        )
        # TODO actually log the data to the run
        # self._client.log_metric(
        #     child_run_1.info.run_id,
        #     "rouge1_mean",
        #     data['rouge']['rouge1_mean'],
        # )

    def get_experiment(self, experiment_id: str) -> dict:
        raise NotImplementedError

    def update_experiment(self, experiment_id: str, new_name: str) -> None:
        raise NotImplementedError

    def list_experiments(self) -> list:
        raise NotImplementedError

    def get_workflow(self, workflow_id: str) -> dict:
        raise NotImplementedError

    def update_workflow(self, workflow_id: str, new_data: dict) -> None:
        raise NotImplementedError

    def delete_workflow(self, workflow_id: str) -> None:
        raise NotImplementedError

    def list_workflows(self, experiment_id: str) -> list:
        raise NotImplementedError

    def update_job(self, job_id: str, new_data: dict):
        raise NotImplementedError

    def get_job(self, job_id: str):
        raise NotImplementedError

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
