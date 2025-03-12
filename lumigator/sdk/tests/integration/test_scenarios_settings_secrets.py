from functools import partial

from lumigator_sdk.lumigator import LumigatorClient
from lumigator_sdk.settings import Secrets
from lumigator_sdk.strict_schemas import SecretUploadRequest


def _test_secret_flow(upload, delete, list_secrets, is_configured):
    # List secrets, should be none.
    secrets = list_secrets()
    assert len(secrets) == 0

    # Create the secret.
    assert upload() is True

    # List secrets, should be one.
    secrets = list_secrets()
    assert len(secrets) == 1

    # Check if the secret is configured.
    assert is_configured() is True

    # Delete the secret.
    assert delete() is True

    # List secrets, should be none.
    secrets = list_secrets()
    assert len(secrets) == 0

    # Check if the secret is configured.
    assert is_configured() is False


def test_settings_secrets_secret(lumi_client_int: LumigatorClient):
    api_key = Secrets.APIKey.OPENAI
    data = SecretUploadRequest(value="test_value", description=api_key.description)

    _test_secret_flow(
        upload=partial(lumi_client_int.settings.secrets.upload_secret, api_key.name, data),
        delete=partial(lumi_client_int.settings.secrets.delete_secret, api_key.name),
        list_secrets=lumi_client_int.settings.secrets.list_secrets,
        is_configured=partial(lumi_client_int.settings.secrets.is_secret_configured, api_key.name),
    )


def test_settings_secrets_create_api_key(lumi_client_int: LumigatorClient):
    api_key = Secrets.APIKey.OPENAI
    data = "test_value"

    _test_secret_flow(
        upload=partial(lumi_client_int.settings.secrets.upload_api_key, api_key, data),
        delete=partial(lumi_client_int.settings.secrets.delete_api_key, api_key),
        list_secrets=lumi_client_int.settings.secrets.list_api_keys,
        is_configured=partial(lumi_client_int.settings.secrets.is_api_key_configured, api_key),
    )
