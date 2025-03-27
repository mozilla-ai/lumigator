import contextlib
from collections.abc import Generator
from typing import Protocol
from uuid import UUID
from warnings import warn

from lumigator_schemas.experiments import GetExperimentResponse
from lumigator_schemas.jobs import JobLogsResponse, JobResults
from lumigator_schemas.tasks import TaskDefinition
from lumigator_schemas.workflows import WorkflowDetailsResponse, WorkflowResponse, WorkflowStatus
from typing_extensions import deprecated

from backend.tracking.schemas import RunOutputs


class TrackingClient(Protocol):
    """Interface for tracking clients."""

    async def create_experiment(
        self,
        name: str,
        description: str,
        task_definition: TaskDefinition,
        dataset: UUID,
        max_samples: int,
    ) -> GetExperimentResponse:
        """Create a new experiment."""
        ...

    async def get_experiment(self, experiment_id: str) -> GetExperimentResponse | None:
        """Get an experiment."""
        ...

    async def update_experiment(self, experiment_id: str, new_name: str) -> None:
        """Update an experiment."""
        ...

    async def delete_experiment(self, experiment_id: str) -> None:
        """Delete an experiment."""
        ...

    async def list_experiments(self, skip: int, limit: int) -> list[GetExperimentResponse]:
        """List all experiments."""
        ...

    async def experiments_count(self) -> int:
        """Count all experiments."""
        ...

    async def create_workflow(
        self, experiment_id: str, description: str, name: str, model: str, system_prompt: str
    ) -> WorkflowResponse:
        """Create a new workflow."""
        ...

    async def get_workflow(self, workflow_id: str) -> WorkflowDetailsResponse | None:
        """Get a workflow."""
        ...

    @deprecated("get_workflow_logs is deprecated, it will be removed in future versions.")
    async def get_workflow_logs(self, workflow_id: str) -> JobLogsResponse:
        """Get workflow logs.

        .. deprecated::
            get_workflow_logs is deprecated, it will be removed in future versions.
        """
        warn(
            "get_workflow_logs is deprecated, it will be removed in future versions.", DeprecationWarning, stacklevel=2
        )
        ...

    async def update_workflow_status(self, workflow_id: str, status: WorkflowStatus) -> None:
        """Update a workflow."""
        ...

    async def delete_workflow(self, workflow_id: str) -> WorkflowResponse:
        """Delete a workflow."""
        ...

    async def list_workflows(self, experiment_id: str) -> list:
        """List all workflows for an experiment."""
        ...

    async def create_job(self, experiment_id: str, workflow_id: str, name: str, job_id: str):
        """Link a started job to an experiment and a workflow."""
        ...

    async def update_workflow(self, workflow_id: str, data: RunOutputs):
        """Update the outputs of a workflow"""
        ...

    async def get_job(self, job_id: str) -> JobResults | None:
        """Get a job."""
        ...

    async def update_job(self, job_id: str, data: RunOutputs):
        """Update a job."""
        ...

    async def delete_job(self, job_id: str) -> None:
        """Delete a job."""
        ...

    async def list_jobs(self, workflow_id: str) -> list:
        """List all jobs for a workflow."""
        ...

    async def is_status_match(self, tracking_client_status: str, workflow_status: WorkflowStatus) -> bool:
        """Checks whether the given tracking client status correctly maps to the specified workflow status.

        :param tracking_client_status: The status understood by the tracking client.
        :param workflow_status: A workflow status to compare against.
        :return: True if the status matches, False otherwise.
        """
        ...

    async def is_status_terminal(self, tracking_client_status: str) -> bool:
        """Checks whether the given tracking client status is terminal.

        :param tracking_client_status: The status understood by the tracking client.
        :return: True if the status is terminal, False otherwise.
        """
        ...


class TrackingClientManager(Protocol):
    """Interface for tracking client managers."""

    @contextlib.contextmanager
    def connect(self) -> Generator[TrackingClient, None, None]:
        """Yield a tracking client, handling exceptions."""
        ...
