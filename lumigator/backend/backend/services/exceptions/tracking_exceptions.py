from backend.services.exceptions.base_exceptions import (
    NotFoundError,
)


class RunNotFoundError(NotFoundError):
    """Raised when a run cannot be found."""

    def __init__(self, resource_id: str, message: str | None = None, exc: Exception | None = None):
        """Creates a RunNotFoundError.

        :param resource_id: ID of run
        :param message: optional error message
        :param exc: optional exception, where possible raise ``from exc`` to preserve the original traceback
        """
        super().__init__("Run", str(resource_id), message, exc)
