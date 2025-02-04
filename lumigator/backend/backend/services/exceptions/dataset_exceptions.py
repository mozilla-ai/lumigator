from uuid import UUID

from backend.services.exceptions.base_exceptions import (
    NotAvailableError,
    NotFoundError,
    UpstreamError,
    ValidationError,
)


class DatasetNotFoundError(NotFoundError):
    """Raised when dataset does not exist."""

    def __init__(self, resource_id: UUID, message: str | None = None, exc: Exception | None = None):
        """Creates a DatasetNotFoundError.

        :param resource_id: UUID of dataset resource
        :param message: optional error message
        :param exc: optional exception
        """
        super().__init__("Dataset", str(resource_id), message, exc)


class DatasetValidationError(ValidationError):
    """Base exception, raised when validation-related errors occur."""

    def __init__(self, message: str, exc: Exception | None = None):
        """Creates a DatasetValidationError.

        :param message: optional error message
        :param exc: optional exception instance
        """
        super().__init__(message, exc)


class DatasetInvalidError(DatasetValidationError):
    """Raised when the dataset is missing required data."""

    def __init__(self, message: str, exc: Exception | None = None):
        """Creates a DatasetInvalidError.

        :param message: optional error message
        :param exc: optional exception
        """
        super().__init__(f"Dataset is invalid: {message}", exc)


class DatasetSizeError(DatasetValidationError):
    """Raised when the file size exceeds the allowed limit."""

    def __init__(self, max_size: str, exc: Exception | None = None):
        """Creates a DatasetSizeError.

        :param max_size: the maximum allowed dataset size
        :param exc: optional exception
        """
        super().__init__(f"Dataset upload exceeds the {max_size} limit", exc)
        self.max_size = max_size


class DatasetMissingFieldsError(DatasetValidationError):
    """Raised when the file is missing required data."""

    def __init__(self, missing_fields: set[str], exc: Exception | None = None):
        """Creates a DatasetMissingFieldsError.

        :param missing_fields: list of distinct fields missing from the dataset
        :param exc: optional exception
        """
        super().__init__(f"Dataset is missing required fields: {', '.join(missing_fields)}", exc)
        self.missing_fields = missing_fields


class DatasetUpstreamError(UpstreamError):
    """Raised when there are issues with upstream services (e.g. S3)."""

    def __init__(self, service_name: str, message: str | None = None, exc: Exception | None = None):
        """Creates a DatasetUpstreamError.

        :param service_name: the name of the service which threw the error
        :param message: an optional error message
        :param exc: optional exception
        """
        super().__init__(service_name, message, exc)


class DatasetNotAvailableError(NotAvailableError):
    """Raised when a dataset is not available.

    This error differs from DatasetNotFoundError, the expectation here is that the dataset
    should have been available based on identifying information for another resource.

    Example: When a job runs to generate a dataset, the job ID may later be used to retrieve
    the dataset.
    """

    def __init__(
        self,
        message: str,
        exc: Exception | None = None,
    ):
        """Creates a DatasetNotAvailableError.

        :param message: error message
        :param exc: optional exception
        """
        super().__init__("Dataset", message, exc)
