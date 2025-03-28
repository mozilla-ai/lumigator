from backend.services.exceptions.base_exceptions import ConflictError, NotFoundError, UpstreamError


class ExperimentNotFoundError(NotFoundError):
    """Raised when an experiment does not exist."""

    def __init__(self, resource_id: str, message: str | None = None, exc: Exception | None = None):
        """Creates a ExperimentNotFoundError.

        :param resource_id: str of experiment resource
        :param message: optional error message
        :param exc: optional exception, where possible raise ``from exc`` to preserve the original traceback
        """
        super().__init__("Experiment", resource_id, message, exc)


class ExperimentConflictError(ConflictError):
    """Raised when conflicts occur as an experiment with the same name already exists."""

    def __init__(self, experiment_name: str, message: str | None = None, exc: Exception | None = None):
        """Creates an ExperimentConflictError.

        :param experiment_name: the name of the conflicting experiment
        :param message: an optional error message
        :param exc: optional exception, where possible raise ``from exc`` to preserve the original traceback
        """
        super().__init__("Experiment", experiment_name, message, exc)


class ExperimentUpstreamError(UpstreamError):
    """Raised when there are issues with upstream services."""

    def __init__(self, service_name: str, message: str | None = None, exc: Exception | None = None):
        """Creates a ExperimentUpstreamError.

        :param service_name: the name of the service which threw the error
        :param message: an optional error message
        :param exc: optional exception, where possible raise ``from exc`` to preserve the original traceback
        """
        super().__init__(service_name, message, exc)
