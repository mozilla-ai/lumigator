import base64

import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from lumigator_schemas.secrets import SecretGetRequest, SecretUploadRequest

from backend.repositories.secrets import SecretRepository
from backend.services.secrets import SecretService


def test_secret_service_valid_key(secret_key, secret_repository):
    """Ensure SecretService initializes correctly with valid keys."""
    service = SecretService(secret_key=secret_key, secret_repo=secret_repository)
    assert isinstance(service, SecretService)
    assert service._secret_key == base64.b64decode(secret_key)


@pytest.mark.parametrize(
    "invalid_secret_key, expected_exception, expected_message",
    [
        ("invalid_base64_string", ValueError, "Unable to decode secret_key, expected base64 encoded value"),
        ("", ValueError, "AES key must be 32 bytes for AES-256 encryption, got: 0"),  # Empty key
        ("shortkey", ValueError, "AES key must be 32 bytes for AES-256 encryption, got: 6"),  # Invalid Base64
        (base64.b64encode(b"short").decode(), ValueError, "AES key must be 32 bytes"),  # Too short
        (base64.b64encode(b"0" * 16).decode(), ValueError, "AES key must be 32 bytes"),  # 16-byte key
        (base64.b64encode(b"0" * 64).decode(), ValueError, "AES key must be 32 bytes"),  # Too long
        (None, TypeError, "Expected secret_key to be a string"),  # Wrong type: None
        (12345, TypeError, "Expected secret_key to be a string"),  # Wrong type: int
    ],
)
def test_secret_service_invalid_key(invalid_secret_key, expected_exception, expected_message, secret_repository):
    """Ensure SecretService raises errors for invalid keys."""
    with pytest.raises(expected_exception, match=expected_message):
        SecretService(secret_key=invalid_secret_key, secret_repo=secret_repository)


@pytest.mark.parametrize(
    "invalid_secret_repo, expected_exception, expected_message",
    [
        (None, TypeError, "Expected secret_repo to be an instance of SecretRepository"),
        (123, TypeError, "Expected secret_repo to be an instance of SecretRepository"),
        ("not_a_repo", TypeError, "Expected secret_repo to be an instance of SecretRepository"),
    ],
)
def test_secret_service_invalid_repository(secret_key, invalid_secret_repo, expected_exception, expected_message):
    """Ensure SecretService raises errors for invalid repositories."""
    with pytest.raises(expected_exception, match=expected_message):
        SecretService(secret_key=secret_key, secret_repo=invalid_secret_repo)


@pytest.mark.parametrize(
    "plaintext",
    [
        "hello world",
        "short",
        "a" * 16,  # Exactly one AES block
        "a" * 31,  # One less than two AES blocks (to test padding)
        "a" * 32,  # Exactly two AES blocks
        "特殊字符!@#$%^&*()",  # Unicode characters
        "",  # Empty string
    ],
)
def test_encrypt_decrypt_round_trip(plaintext, secret_service):
    """Ensure that encrypting and then decrypting returns the original plaintext."""
    encrypted = secret_service._encrypt(plaintext)
    decrypted = secret_service._decrypt(encrypted)
    assert decrypted == plaintext


@pytest.mark.parametrize(
    "invalid_encrypted_text",
    [
        "not_base64_encoded!",
        base64.b64encode(b"short_iv").decode(),  # Less than 16 bytes IV
        base64.b64encode(b"0" * 15).decode(),  # 15-byte IV (invalid)
        base64.b64encode(b"0" * 17).decode(),  # 17-byte IV (invalid)
        base64.b64encode(b"0" * (16 + 15)).decode(),  # IV + non-multiple of block size
    ],
)
def test_decrypt_invalid_ciphertext(invalid_encrypted_text, secret_service):
    """Ensure decrypt raises an error for invalid ciphertext."""
    with pytest.raises(ValueError):
        secret_service._decrypt(invalid_encrypted_text)


def test_encrypt_output_format(secret_service):
    """Ensure encrypt returns a valid base64 string."""
    encrypted = secret_service._encrypt("test")
    assert isinstance(encrypted, str)

    # Ensure it can be decoded as base64
    decoded = base64.b64decode(encrypted)
    assert len(decoded) > 16  # At minimum, must contain IV (16 bytes) + at least one block


@pytest.mark.parametrize(
    "plaintext",
    [
        "hello",  # Not a multiple of 16
        "a" * 16,  # Exactly one AES block
        "a" * 31,  # One less than two blocks
        "a" * 32,  # Exactly two blocks
    ],
)
def test_encrypt_padding(plaintext, secret_service):
    """Ensure AES encryption correctly applies PKCS7 padding."""
    encrypted = secret_service._encrypt(plaintext)
    decoded = base64.b64decode(encrypted)

    # Extract IV and ciphertext
    ciphertext = decoded[16:]

    # Ensure ciphertext length is a multiple of AES block size
    assert len(ciphertext) % 16 == 0

    # Verify padding explicitly
    cipher = Cipher(algorithms.AES(secret_service._secret_key), modes.CBC(decoded[:16]), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()

    # Check PKCS7 padding
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

    # Ensure original plaintext is recovered
    assert decrypted.decode() == plaintext


def test_secret_upload_request(
    secret_service: SecretService, secret_repository: SecretRepository, dependency_overrides_fakes
):
    """Ensure that uploads are successfully stored encrypted, and indicate they're created initially, but
    updated on subsequent uploads
    """

    # Reusable way to assert our logic
    def upload_and_assert(name: str, request: SecretUploadRequest, expect_created: bool):
        # Capture the value as it gets encrypted
        original_value = request.value
        # Create the secret
        is_created = secret_service.upload_secret(name, request)
        assert is_created == expect_created
        # We should now have some data (1 secret)
        assert secret_repository.list() != []
        assert len(secret_repository.list()) == 1
        # Verify the secret that was stored has the right values (and an encrypted secret)
        db_secret = secret_repository.list()[0]
        assert db_secret.name == name.lower()
        assert db_secret.value != original_value
        # Decrypt to ensure it is symmetrical
        assert secret_service._decrypt(db_secret.value) == original_value
        assert db_secret.description == request.description

    # Check we have nothing in storage to start
    assert secret_repository.list() == []

    # Secret name
    name = "TEST_AI_CLIENT_KEY"  # pragma: allowlist secret

    # First time we upload the secret it's created
    upload_and_assert(name, SecretUploadRequest(value="123456", description="test secret"), True)
    # Second time it's updated (we can change the value of the secret)
    upload_and_assert(name, SecretUploadRequest(value="abcdef", description="2nd desc"), False)


def test_secret_list_with_value(secret_service: SecretService, secret_repository: SecretRepository):
    """Ensure that we can list the name (and description) of configured secrets, but not their values."""
    secret_1_name = "TEST_AI_API_KEY"  # pragma: allowlist secret
    secret_1_desc = "test secret"  # pragma: allowlist secret

    secret_2_name = "TEST_OTHER_API_KEY"  # pragma: allowlist secret
    secret_2_desc = "very important secret"  # pragma: allowlist secret

    # Ensure we have no secrets to start
    assert secret_repository.list() == []
    assert secret_service.list_secrets() == []

    # Create a secret
    secret_service.upload_secret(secret_1_name, SecretUploadRequest(value="123456", description=secret_1_desc))

    # Check we have some data (1 secret)
    assert len(secret_repository.list()) == 1

    # List secrets and ensure we get the name and description
    secrets = secret_service.list_secrets()
    assert len(secrets) == 1
    assert secrets[0].name == secret_1_name.lower()
    assert secrets[0].description == secret_1_desc

    # Create another secret
    secret_service.upload_secret(secret_2_name, SecretUploadRequest(value="123456", description=secret_2_desc))

    # List secrets and ensure we now have 2 and both names
    secrets = secret_service.list_secrets()
    assert len(secrets) == 2
    secret_names = {secret.name.lower() for secret in secrets}
    assert secret_1_name.lower() in secret_names
    assert secret_2_name.lower() in secret_names


def test_secret_delete(secret_service: SecretService, secret_repository: SecretRepository):
    """Ensure that we can delete a secret by name."""
    secret_name = "TEST_AI_API_KEY"  # pragma: allowlist secret

    # Ensure we have no secrets to start
    assert secret_repository.list() == []
    assert secret_service.list_secrets() == []

    # Create a secret
    secret_service.upload_secret(secret_name, SecretUploadRequest(value="123456", description="test desc"))

    # Check we have some data (1 secret)
    assert len(secret_repository.list()) == 1
    secrets = secret_service.list_secrets()
    assert len(secrets) == 1
    assert secrets[0].name == secret_name.lower()

    # Delete the secret
    res = secret_service.delete_secret(secret_name)
    assert res is True
    assert secret_repository.list() == []
    assert secret_service.list_secrets() == []

    # Delete the secret again (should return False)
    res = secret_service.delete_secret(secret_name)
    assert res is False
    assert secret_repository.list() == []
    assert secret_service.list_secrets() == []


def test_secret_existence(secret_service: SecretService):
    secret_service.upload_secret("valid_secret", SecretUploadRequest(value="123456", description="test desc"))
    assert secret_service.is_secret_configured("valid_secret") is True
    assert secret_service.is_secret_configured("invalid_secret") is False
