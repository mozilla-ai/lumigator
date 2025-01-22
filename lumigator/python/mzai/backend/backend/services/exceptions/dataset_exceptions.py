from uuid import UUID

from backend.services.exceptions.base_exceptions import (
    NotFoundError,
    UpstreamError,
    ValidationError,
)


class DatasetNotFoundError(NotFoundError):
    """Raised when dataset does not exist."""

    def __init__(self, resource_id: UUID, message: str | None = None):
        super().__init__("Dataset", str(resource_id), message)


class DatasetValidationError(ValidationError):
    """Base exception, raised when validation-related errors occur.

    :param message: an optional error message
    """

    def __init__(self, message: str):
        super().__init__(message)


class DatasetInvalidError(DatasetValidationError):
    """Raised when the dataset is missing required data.

    :param message: an optional error message
    """

    def __init__(self, message: str):
        super().__init__(f"Dataset is invalid: {message}")


class DatasetSizeError(DatasetValidationError):
    """Raised when the file size exceeds the allowed limit.

    :param max_size: the maximum allowed dataset size
    """

    def __init__(self, max_size: str):
        super().__init__(f"Dataset upload exceeds the {max_size} limit")
        self.max_size = max_size


class DatasetMissingFieldsError(DatasetValidationError):
    """Raised when the file is missing required data.

    :param missing_fields: list of distinct fields missing from the dataset
    """

    def __init__(self, missing_fields: set[str]):
        super().__init__(f"Dataset is missing required fields: {', '.join(missing_fields)}")
        self.missing_fields = missing_fields


class DatasetUpstreamError(UpstreamError):
    """Raised when there are issues with upstream services (e.g. S3).

    :param service_name: the name of the service which threw the error
    :param original_exception: the original exception which was raised
    :param message: an optional error message
    """

    def __init__(
        self, service_name: str, original_exception: Exception, message: str | None = None
    ):
        super().__init__(service_name, original_exception, message)
