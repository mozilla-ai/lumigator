from backend.services.exceptions.base_exceptions import NotFoundError, ValidationError


class WorkflowNotFoundError(NotFoundError):
    """Raised when a workflow does not exist."""

    def __init__(self, resource_id: str, message: str | None = None, exc: Exception | None = None):
        """Creates a WorkflowNotFoundError.

        :param resource_id: UUID of workflow resource
        :param message: optional error message
        :param exc: optional exception
        """
        super().__init__("Workflow", str(resource_id), message, exc)


class WorkflowValidationError(ValidationError):
    """Base exception, raised when validation-related errors occur."""

    def __init__(self, message: str, exc: Exception | None = None):
        """Creates a WorkflowValidationError.

        :param message: optional error message
        :param exc: optional exception instance
        """
        super().__init__(message, exc)
