from uuid import UUID

from backend.services.exceptions.base_exceptions import NotFoundError


class ExperimentNotFoundError(NotFoundError):
    """Raised when an experiment does not exist."""

    def __init__(self, resource_id: UUID, message: str | None = None, exc: Exception | None = None):
        """Creates a ExperimentNotFoundError.

        :param resource_id: UUID of experiment resource
        :param message: optional error message
        :param exc: optional exception
        """
        super().__init__("Job", str(resource_id), message, exc)
