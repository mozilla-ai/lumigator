from uuid import UUID

from lumigator_schemas.jobs import JobType

from backend.services.exceptions.base_exceptions import (
    NotFoundError,
    ServiceError,
    UpstreamError,
    ValidationError,
    _append_message,
)


class JobNotFoundError(NotFoundError):
    """Raised when a job does not exist."""

    def __init__(self, resource_id: UUID, message: str | None = None, exc: Exception | None = None):
        """Creates a JobNotFoundError.

        :param resource_id: UUID of job resource
        :param message: optional error message
        :param exc: optional exception
        """
        super().__init__("Job", str(resource_id), message, exc)


class JobTypeUnsupportedError(ServiceError):
    """Raised when a job type is not yet supported."""

    def __init__(self, job_type: JobType | object, message: str | None = None, exc: Exception | None = None):
        """Creates a JobTypeNotSupportedError

        :param job_type: the type of job that is not supported,
            either a JobType or the creation request
        :param message: optional error message
        :param exc: optional exception
        """
        if isinstance(job_type, JobType):
            job_type_name = job_type.name
        else:
            job_type_name = type(job_type).__name__

        msg = _append_message(f"Job type '{job_type}' not yet supported", message)
        super().__init__(msg, exc)
        self.job_type = job_type
        self.job_type_name = job_type_name


class JobUpstreamError(UpstreamError):
    """Raised when there are issues with upstream services (e.g. Ray)."""

    def __init__(self, service_name: str, message: str | None = None, exc: Exception | None = None):
        """Creates a JobUpstreamError.

        :param service_name: the name of the service which threw the error
        :param message: an optional error message
        :param exc: optional exception
        """
        super().__init__(service_name, message, exc)


class JobValidationError(ValidationError):
    """Raised when there are issues during Job validation."""

    def __init__(self, message: str, exc: Exception | None = None):
        """Creates a JobValidationError

        :param message: an optional error message
        :param exc: optional exception
        """
        super().__init__(message, exc)
