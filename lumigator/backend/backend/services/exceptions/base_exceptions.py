def _append_message(existing: str, message: str | None) -> str:
    """Appends a message to the existing message if it exists."""
    return f"{existing}{f': {message}' if message else ''}"


class ServiceError(Exception):
    """Base exception for service-related errors."""

    def __init__(self, message: str, exc: Exception | None = None):
        """Creates a ServiceError.

        :param message: error message
        :param exc: optional exception
        """
        self.message = message
        self.exc = exc


class NotFoundError(ServiceError):
    """Base exception for errors caused by a resource that cannot be found."""

    def __init__(
        self,
        resource: str,
        resource_id: str,
        message: str | None = None,
        exc: Exception | None = None,
    ):
        """Creates a NotFoundError.

        :param resource: the resource that was not found
        :param resource_id: the ID of the resource that was not found
        :param message: an optional error message
        :param exc: optional exception
        """
        msg = f"{resource} with ID {resource_id} not found"
        super().__init__(_append_message(msg, message), exc)
        self.resource = resource
        self.resource_id = resource_id


class ValidationError(ServiceError):
    """Base exception for validation-related errors."""

    def __init__(self, message: str | None = None, exc: Exception | None = None):
        """Creates a ValidationError

        :param message: optional error message
        :param exc: optional exception
        """
        super().__init__(message, exc)


class UpstreamError(ServiceError):
    """Base exception for upstream-related errors."""

    def __init__(self, service_name: str, message: str | None = None, exc: Exception | None = None):
        """Creates a UpstreamError.

        :param service_name: the name of the service which threw the error
        :param message: an optional error message
        :param exc: optional exception
        """
        msg = _append_message(f"Upstream error with {service_name}", message)
        super().__init__(msg, exc)
        self.service_name = service_name


class NotAvailableError(ServiceError):
    """Base exception for errors caused by a resource not being available."""

    def __init__(
        self,
        resource: str,
        message: str,
        exc: Exception | None = None,
    ):
        """Creates a NotAvailableError.

        :param resource: the resource type that was not available
        :param message: error message
        :param exc: optional exception
        """
        msg = f"{resource} not available"
        super().__init__(_append_message(msg, message), exc)
        self.resource = resource
