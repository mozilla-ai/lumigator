from lumigator_schemas.secrets import SecretUploadRequest

from backend.repositories.secrets import SecretRepository
from backend.services.secrets import SecretService


def test_secret_upload_request(
    secret_service: SecretService, secret_repository: SecretRepository, dependency_overrides_fakes
):
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
        assert db_secret.name == name
        assert db_secret.value != original_value
        # Decrypt to ensure it is symmetrical
        assert secret_service.decrypt(db_secret.value) == original_value
        assert db_secret.description == request.description

    # Check we have nothing in storage to start
    assert secret_repository.list() == []

    # Secret name
    name = "TEST_AI_CLIENT_KEY"  # pragma: allowlist secret

    # First time we upload the secret it's created
    upload_and_assert(name, SecretUploadRequest(value="123456", description="test secret"), True)
    # Second time it's updated (we can change the value of the secret)
    upload_and_assert(name, SecretUploadRequest(value="abcdef", description="2nd desc"), False)
