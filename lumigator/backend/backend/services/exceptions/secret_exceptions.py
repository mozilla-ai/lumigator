from backend.services.exceptions.base_exceptions import ValidationError


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
