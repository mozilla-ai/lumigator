import base64
import binascii
import os

from cryptography.exceptions import InvalidKey
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from lumigator_schemas.secrets import SecretGetRequest, SecretUploadRequest

from backend.repositories.secrets import SecretRepository
from backend.services.exceptions.secret_exceptions import SecretDecryptionError, SecretEncryptionError


class SecretService:
    def __init__(self, secret_key: str, secret_repo: SecretRepository):
        if not isinstance(secret_key, str):
            raise TypeError(f"Expected secret_key to be a string, got {type(secret_key).__name__}")
        if not isinstance(secret_repo, SecretRepository):
            raise TypeError("Expected secret_repo to be an instance of SecretRepository") from None

        try:
            aes_key = base64.b64decode(secret_key)
        except binascii.Error as e:
            raise ValueError("Unable to decode secret_key, expected base64 encoded value") from e

        # Ensure the key is 32 bytes (AES-256)
        if len(aes_key) != 32:
            raise ValueError(f"AES key must be 32 bytes for AES-256 encryption, got: {len(aes_key)}") from None

        self._secret_key = aes_key
        self._secret_repo = secret_repo

    def _get_secret_by_name(self, name: str) -> SecretGetRequest | None:
        return self._secret_repo.get_secret_by_name(name)

    def upload_secret(self, name: str, secret_upload_request: SecretUploadRequest) -> bool:
        """Uploads a secret for the specified name.

        :param name: The name of the secret to be uploaded
        :param secret_upload_request: The secret upload request containing the secret data
        :return: boolean value indicating whether the secret is newly created (false if it already existed)
        """
        # Encrypt the value
        try:
            secret_upload_request.value = self._encrypt(secret_upload_request.value)
        except (TypeError, ValueError) as e:
            raise SecretEncryptionError(name) from e

        # Save the secret via the repository
        secret_dict = secret_upload_request.model_dump()
        secret_dict["name"] = name

        return self._secret_repo.save_secret(name, secret_dict)

    def get_decrypted_secret_value(self, name: str) -> str | None:
        """Gets a decrypted value for the secret specified by name.

        NOTE: Decrypted secrets must be treated carefully and never exposed to the end user.

        :param name: The name of the secret to be decrypted
        :return: The decrypted secret or None if no secret was found
        :raises SecretDecryptionError: raised if there are issues during decryption
        """
        try:
            record = self._secret_repo.get_secret_by_name(name)
            if record is None:
                return None
        except ValueError as e:
            raise SecretDecryptionError(name) from e

    # AES requires a 16-byte Initialization Vector (IV)
    @staticmethod
    def generate_iv():
        return os.urandom(16)

    def _encrypt(self, plaintext: str) -> str:
        """Encrypts a plaintext string using AES in CBC mode with PKCS7 padding.

        The method applies PKCS7 padding to the plaintext, encrypts it using AES-CBC,
        and returns a base64-encoded string containing the IV and ciphertext.

        :param plaintext: The plaintext string to encrypt.
        :return: A base64-encoded string containing the IV followed by the encrypted ciphertext.
        :raises TypeError: If the input plaintext is not a string.
        :raises ValueError: If encryption fails due to an invalid key or another issue.
        """
        if not isinstance(plaintext, str):
            raise TypeError("Plaintext must be a string")

        try:
            iv = SecretService.generate_iv()
            cipher = Cipher(algorithms.AES(self._secret_key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()

            # Apply PKCS7 padding to ensure plaintext is a multiple of block size (16 bytes)
            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_plaintext = padder.update(plaintext.encode()) + padder.finalize()

            ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

            return base64.b64encode(iv + ciphertext).decode()
        except InvalidKey as e:
            raise ValueError("Encryption failed due to an invalid key") from e
        except (ValueError, AttributeError, Exception) as e:
            raise ValueError(f"Encryption failed: {e}") from e

    def _decrypt(self, encrypted_text: str) -> str:
        """Decrypts a base64 encoded, AES-encrypted string using the secret key.

        This method decodes the base64-encoded encrypted text, decrypts it using AES in CBC mode,
        removes PKCS7 padding, and returns the decrypted plaintext.

        :param encrypted_text: The base64-encoded string containing the encrypted text.
            It is expected to be encrypted using AES with a secret key and CBC mode.
        :return: The decrypted plaintext data as a UTF-8 string.
        :raises ValueError: If the decryption process fails, including invalid base64 encoding or AES decryption issues.
        """
        try:
            # Decode the base64 encoded string
            data = base64.b64decode(encrypted_text)
            iv, ciphertext = data[:16], data[16:]

            # Set up the decryption cipher
            cipher = Cipher(algorithms.AES(self._secret_key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()

            # Decrypt and finalize
            decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()

            # Remove PKCS7 padding
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

            return decrypted.decode()

        except (base64.binascii.Error, ValueError) as e:
            raise ValueError("Failed to decode the encrypted text") from e
        except Exception as e:
            # Catch any cryptography or padding related issues
            raise ValueError("Decryption failed") from e
