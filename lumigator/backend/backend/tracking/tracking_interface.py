import contextlib
from abc import ABC, abstractmethod
from collections.abc import Generator


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
    def create_experiment(self, name: str) -> str:
        """Create a new experiment."""
        pass

    @abstractmethod
    def get_experiment(self, experiment_id: str) -> dict:
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
    def list_experiments(self) -> list:
        """List all experiments."""
        pass

    @abstractmethod
    def create_workflow(self, experiment_id: str) -> str:
        """Create a new workflow."""
        pass

    @abstractmethod
    def get_workflow(self, workflow_id: str) -> dict:
        """Get a workflow."""
        pass

    @abstractmethod
    def update_workflow(self, workflow_id: str, new_data: dict) -> None:
        """Update a workflow."""
        pass

    @abstractmethod
    def delete_workflow(self, workflow_id: str) -> None:
        """Delete a workflow."""
        pass

    @abstractmethod
    def list_workflows(self, experiment_id: str) -> list:
        """List all workflows for an experiment."""
        pass

    @abstractmethod
    def create_job(self, experiment_id: str, workflow_id: str, data: dict):
        """Log the job output."""
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> dict:
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
