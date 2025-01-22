def _append_message(existing: str, message: str | None) -> str:
    """Appends a message to the existing message if it exists."""
    return f"{existing}{f': {message}' if message else ''}"


class ServiceError(Exception):
    """Base exception for service-related errors."""

    def __init__(self, message: str):
        self.message = message
        pass


class NotFoundError(ServiceError):
    """Base exception for errors caused by a resource that cannot be found.

    :param resource: the resource that was not found
    :param resource_id: the ID of the resource that was not found
    :param message: an optional error message
    """

    def __init__(self, resource: str, resource_id: str, message: str | None = None):
        msg = f"{resource} with ID {resource_id} not found"
        super().__init__(_append_message(msg, message))
        self.resource = resource
        self.resource_id = resource_id


class ValidationError(ServiceError):
    """Base exception for validation-related errors.

    :param message: an optional error message
    """

    def __init__(self, message: str | None = None):
        super().__init__(message)


class UpstreamError(ServiceError):
    """Base exception for upstream-related errors.

    :param service_name: the name of the service which threw the error
    :param original_exception: the original exception which was raised
    :param message: an optional error message
    """

    def __init__(
        self, service_name: str, original_exception: Exception, message: str | None = None
    ):
        msg = _append_message(f"Upstream error with {service_name}", message)
        super().__init__(msg)
        self.service_name = service_name
        self.original_exception = original_exception
