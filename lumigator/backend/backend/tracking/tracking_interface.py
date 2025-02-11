import contextlib
from abc import ABC, abstractmethod
from collections.abc import Generator

from lumigator_schemas.experiments import GetExperimentResponse
from lumigator_schemas.jobs import JobLogsResponse, JobResults
from lumigator_schemas.workflows import WorkflowDetailsResponse, WorkflowResponse, WorkflowStatus

from backend.tracking.schemas import RunOutputs


class TrackingClientManager(ABC):
    """Abstract base class for tracking client managers."""

    def __init__(self, tracking_uri: str):
        self._tracking_uri = tracking_uri

    @contextlib.contextmanager
    @abstractmethod
    def connect(self) -> Generator:
        """Yield a tracking client, handling exceptions."""
        pass


class TrackingClient(ABC):
    """Abstract base class for tracking clients."""

    @abstractmethod
    def create_experiment(self, name: str, description: str) -> GetExperimentResponse:
        """Create a new experiment."""
        pass

    @abstractmethod
    def get_experiment(self, experiment_id: str) -> GetExperimentResponse | None:
        """Get an experiment."""
        pass

    @abstractmethod
    def update_experiment(self, experiment_id: str, new_name: str) -> None:
        """Update an experiment."""
        pass

    @abstractmethod
    def delete_experiment(self, experiment_id: str) -> None:
        """Delete an experiment."""
        pass

    @abstractmethod
    def list_experiments(self, skip: int, limit: int) -> list[GetExperimentResponse]:
        """List all experiments."""
        pass

    @abstractmethod
    def experiments_count(self) -> int:
        """Count all experiments."""
        pass

    @abstractmethod
    def create_workflow(self, experiment_id: str, description: str, name: str) -> WorkflowResponse:
        """Create a new workflow."""
        pass

    @abstractmethod
    def get_workflow(self, workflow_id: str) -> WorkflowDetailsResponse | None:
        """Get a workflow."""
        pass

    @abstractmethod
    def get_workflow_logs(self, workflow_id: str) -> JobLogsResponse:
        """Get a workflow logs."""
        pass

    @abstractmethod
    def update_workflow_status(self, workflow_id: str, status: WorkflowStatus) -> None:
        """Update a workflow."""
        pass

    @abstractmethod
    def delete_workflow(self, workflow_id: str) -> WorkflowResponse:
        """Delete a workflow."""
        pass

    @abstractmethod
    def list_workflows(self, experiment_id: str) -> list:
        """List all workflows for an experiment."""
        pass

    @abstractmethod
    def create_job(self, experiment_id: str, workflow_id: str, name: str, data: RunOutputs):
        """Log the job output."""
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> JobResults | None:
        """Get a job."""
        pass

    @abstractmethod
    def update_job(self, job_id: str, new_data: dict) -> None:
        """Update a job."""
        pass

    @abstractmethod
    def delete_job(self, job_id: str) -> None:
        """Delete a job."""
        pass

    @abstractmethod
    def list_jobs(self, experiment_id: str, workflow_id: str) -> list:
        """List all jobs for an workflow."""
        pass
