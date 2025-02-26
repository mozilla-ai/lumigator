import contextlib
from collections.abc import Generator
from typing import Protocol
from uuid import UUID

from lumigator_schemas.experiments import GetExperimentResponse
from lumigator_schemas.jobs import JobLogsResponse, JobResults
from lumigator_schemas.tasks import TaskType
from lumigator_schemas.workflows import WorkflowDetailsResponse, WorkflowResponse, WorkflowStatus

from backend.tracking.schemas import RunOutputs


class TrackingClient(Protocol):
    """Interface for tracking clients."""

    def create_experiment(
        self, name: str, description: str, task: TaskType, dataset: UUID, max_samples: int
    ) -> GetExperimentResponse:
        """Create a new experiment."""
        ...

    def get_experiment(self, experiment_id: str) -> GetExperimentResponse | None:
        """Get an experiment."""
        ...

    def update_experiment(self, experiment_id: str, new_name: str) -> None:
        """Update an experiment."""
        ...

    def delete_experiment(self, experiment_id: str) -> None:
        """Delete an experiment."""
        ...

    def list_experiments(self, skip: int, limit: int) -> list[GetExperimentResponse]:
        """List all experiments."""
        ...

    def experiments_count(self) -> int:
        """Count all experiments."""
        ...

    def create_workflow(self, experiment_id: str, description: str, name: str, model: str) -> WorkflowResponse:
        """Create a new workflow."""
        ...

    def get_workflow(self, workflow_id: str) -> WorkflowDetailsResponse | None:
        """Get a workflow."""
        ...

    def get_workflow_logs(self, workflow_id: str) -> JobLogsResponse:
        """Get workflow logs."""
        ...

    def update_workflow_status(self, workflow_id: str, status: WorkflowStatus) -> None:
        """Update a workflow."""
        ...

    def delete_workflow(self, workflow_id: str) -> WorkflowResponse:
        """Delete a workflow."""
        ...

    def list_workflows(self, experiment_id: str) -> list:
        """List all workflows for an experiment."""
        ...

    def create_job(self, experiment_id: str, workflow_id: str, name: str, data: RunOutputs) -> None:
        """Log the job output."""
        ...

    def get_job(self, job_id: str) -> JobResults | None:
        """Get a job."""
        ...

    def update_job(self, job_id: str, new_data: dict) -> None:
        """Update a job."""
        ...

    def delete_job(self, job_id: str) -> None:
        """Delete a job."""
        ...

    def list_jobs(self, experiment_id: str, workflow_id: str) -> list:
        """List all jobs for a workflow."""
        ...


class TrackingClientManager(Protocol):
    """Interface for tracking client managers."""

    @contextlib.contextmanager
    def connect(self) -> Generator[TrackingClient, None, None]:
        """Yield a tracking client, handling exceptions."""
        ...
