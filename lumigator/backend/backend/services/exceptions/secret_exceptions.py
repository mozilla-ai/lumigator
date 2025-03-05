from backend.services.exceptions.base_exceptions import NotFoundError, ValidationError


class SecretEncryptionError(ValidationError):
    """Raised when there are issues during encryption of a secret."""

    def __init__(self, name: str, exc: Exception | None = None):
        """Creates a SecretEncryptionError

        :param name: the name of the secret that caused the error
        :param exc: optional exception
        """
        super().__init__(f"Error encrypting secret: {name}", exc)


class SecretDecryptionError(ValidationError):
    """Raised when there are issues during decryption of a secret."""

    def __init__(self, name: str, exc: Exception | None = None):
        """Creates a SecretDecryptionError

        :param name: the name of the secret that caused the error
        :param exc: optional exception
        """
        super().__init__(f"Error decrypting secret: {name}", exc)


class SecretNotFoundError(NotFoundError):
    """Raised when the specified secret is not found in the secrets repository."""

    def __init__(self, resource_id, message: str = "", exc: Exception | None = None):
        """Creates a SecretNotFoundError

        :param resource_id: the name of the secret that was not found
        :param exc: optional exception
        """
        super().__init__("Secret", str(resource_id), message, exc)
