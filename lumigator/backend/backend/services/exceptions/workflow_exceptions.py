from backend.services.exceptions.base_exceptions import NotFoundError


class WorkflowNotFoundError(NotFoundError):
    """Raised when an workflow does not exist."""

    def __init__(self, resource_id: str, message: str | None = None, exc: Exception | None = None):
        """Creates a WorkflowNotFoundError.

        :param resource_id: UUID of workflow resource
        :param message: optional error message
        :param exc: optional exception
        """
        super().__init__("Job", str(resource_id), message, exc)
