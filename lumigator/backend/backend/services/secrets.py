import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from lumigator_schemas.secrets import SecretGetRequest, SecretUploadRequest

from backend.repositories.secrets import SecretRepository


class SecretService:
    def __init__(self, secret_key: str, secret_repo: SecretRepository):
        aes_key = base64.b64decode(secret_key)

        # Ensure the key is 32 bytes (AES-256)
        if len(aes_key) != 32:
            raise ValueError(f"AES key must be 32 bytes for AES-256 encryption, got: {len(aes_key)}")

        self._secret_key = aes_key
        self._secret_repo = secret_repo

    def _get_secret_by_name(self, name: str) -> SecretGetRequest | None:
        return self._secret_repo.get_secret_by_name(name)

    def upload_secret(self, name: str, secret_upload_request: SecretUploadRequest) -> bool:
        """Uploads a secret for the specified name.

        @returns bool: indicating whether the secret is newly created (false if it already existed).
        """
        existing_secret = self._get_secret_by_name(name)

        # Encrypt the value
        secret_upload_request.value = self.encrypt(secret_upload_request.value)
        secret_dict = secret_upload_request.model_dump()
        secret_dict["name"] = name

        if existing_secret:
            self._secret_repo.update(existing_secret.id, **secret_dict)
        else:
            self._secret_repo.create(**secret_dict)

        return not bool(existing_secret)

    # AES requires a 16-byte Initialization Vector (IV)
    @staticmethod
    def generate_iv():
        return os.urandom(16)

    def encrypt(self, plaintext: str) -> str:
        iv = SecretService.generate_iv()
        cipher = Cipher(algorithms.AES(self._secret_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        # Ensure the plaintext is a multiple of the block size (16 bytes for AES)
        padding_length = 16 - (len(plaintext) % 16)
        padded_plaintext = plaintext + chr(padding_length) * padding_length
        ciphertext = encryptor.update(padded_plaintext.encode()) + encryptor.finalize()

        return base64.b64encode(iv + ciphertext).decode()

    def decrypt(self, encrypted_text: str) -> str:
        data = base64.b64decode(encrypted_text)
        iv, ciphertext = data[:16], data[16:]
        cipher = Cipher(algorithms.AES(self._secret_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
        # Remove padding
        padding_length = decrypted_padded[-1]

        return decrypted_padded[:-padding_length].decode()
