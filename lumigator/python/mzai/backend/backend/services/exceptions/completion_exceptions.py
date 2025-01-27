from backend.services.exceptions.base_exceptions import UpstreamError


class CompletionUpstreamError(UpstreamError):
    """Raised when there are issues with upstream services (e.g. Mistral or OpenAI)."""

    def __init__(self, service_name: str, message: str | None = None, exc: Exception | None = None):
        """Creates a CompletionUpstreamError.

        :param service_name: the name of the service which threw the error
        :param message: an optional error message
        :param exc: optional exception
        """
        super().__init__(service_name, message, exc)
