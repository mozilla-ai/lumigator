from backend.services.exceptions.base_exceptions import (
    NotAvailableError,
    NotFoundError,
    ValidationError,
)


class WorkflowNotFoundError(NotFoundError):
    """Raised when a workflow does not exist."""

    def __init__(self, resource_id: str, message: str | None = None, exc: Exception | None = None):
        """Creates a WorkflowNotFoundError.

        :param resource_id: UUID of workflow resource
        :param message: optional error message
        :param exc: optional exception, where possible raise ``from exc`` to preserve the original traceback
        """
        super().__init__("Workflow", str(resource_id), message, exc)


class WorkflowDownloadNotAvailableError(NotAvailableError):
    """Raised when the download for a workflow is not available."""

    def __init__(self, resource_id: str, message: str | None = None, exc: Exception | None = None):
        """Creates a WorkflowDownloadNotAvailableError.

        :param resource_id: UUID of workflow resource for which the download is not available
        :param message: optional error message
        :param exc: optional exception, where possible raise ``from exc`` to preserve the original traceback
        """
        msg = self._append_message(f"Workflow {resource_id}", message)
        super().__init__("Workflow download", msg, exc)


class WorkflowValidationError(ValidationError):
    """Base exception, raised when validation-related errors occur."""

    def __init__(self, message: str, exc: Exception | None = None):
        """Creates a WorkflowValidationError.

        :param message: optional error message
        :param exc: optional exception, where possible raise ``from exc`` to preserve the original traceback
        """
        super().__init__(message, exc)
