from http import HTTPStatus

import pytest
from lumigator_sdk.settings import Secrets
from lumigator_sdk.strict_schemas import SecretGetRequest, SecretUploadRequest


@pytest.mark.parametrize(
    "json_data, expected_result",
    [
        (
            [
                {"name": "hf_api_key", "description": "Hugging Face API key"},
                {"name": "deepseek_api_key", "description": "DeepSeek API key"},
            ],
            [
                SecretGetRequest(name="hf_api_key", description="Hugging Face API key"),
                SecretGetRequest(name="deepseek_api_key", description="DeepSeek API key"),
            ],
        )
    ],
)
def test_settings_secret_list(lumi_client, request_mock, json_data, expected_result):
    request_mock.get(
        url=lumi_client.client._api_url + "/settings/secrets",
        status_code=HTTPStatus.OK,
        json=json_data,
    )

    secrets = lumi_client.settings.secrets.list_secrets()
    assert len(secrets) == len(expected_result)
    assert secrets == expected_result


@pytest.mark.parametrize(
    "json_data, expected_result",
    [
        (
            [
                {"name": "hf_api_key", "description": "Hugging Face API key"},
                {"name": "deepseek_api_key", "description": "DeepSeek API key"},
                {"name": "very_important_name", "description": "Something unrelated"},
            ],
            [
                SecretGetRequest(name="hf_api_key", description="Hugging Face API key"),
                SecretGetRequest(name="deepseek_api_key", description="DeepSeek API key"),
            ],
        )
    ],
)
def test_settings_secret_list_api_keys(lumi_client, request_mock, json_data, expected_result):
    request_mock.get(
        url=lumi_client.client._api_url + "/settings/secrets",
        status_code=HTTPStatus.OK,
        json=json_data,
    )

    secrets = lumi_client.settings.secrets.list_api_keys()
    assert len(secrets) == len(expected_result)
    assert secrets == expected_result


@pytest.mark.parametrize(
    "secret_name, json_data, expected_result",
    [
        (
            "hf_api_key",
            [
                {"name": "hf_api_key", "description": "Hugging Face API key"},
                {"name": "deepseek_api_key", "description": "DeepSeek API key"},
            ],
            True,
        ),
        (
            "openai_api_key",
            [
                {"name": "hf_api_key", "description": "Hugging Face API key"},
                {"name": "deepseek_api_key", "description": "DeepSeek API key"},
            ],
            False,
        ),
    ],
)
def test_is_secret_configured(lumi_client, request_mock, secret_name, json_data, expected_result):
    # Mocking the GET request to list secrets
    request_mock.get(
        url=lumi_client.client._api_url + "/settings/secrets",
        status_code=HTTPStatus.OK,
        json=json_data,
    )

    result = lumi_client.settings.secrets.is_secret_configured(secret_name)
    assert result == expected_result


@pytest.mark.parametrize(
    "api_key, json_data, expected_result",
    [
        (
            Secrets.APIKey.HF,
            [
                {"name": "hf_api_key", "description": "Hugging Face API key"},
                {"name": "deepseek_api_key", "description": "DeepSeek API key"},
            ],
            True,
        ),
        (
            Secrets.APIKey.OPENAI,
            [
                {"name": "hf_api_key", "description": "Hugging Face API key"},
                {"name": "deepseek_api_key", "description": "DeepSeek API key"},
            ],
            False,
        ),
    ],
)
def test_is_api_key_configured(lumi_client, request_mock, api_key, json_data, expected_result):
    # Mocking the GET request to list secrets
    request_mock.get(
        url=lumi_client.client._api_url + "/settings/secrets",
        status_code=HTTPStatus.OK,
        json=json_data,
    )

    result = lumi_client.settings.secrets.is_api_key_configured(api_key)
    assert result == expected_result


@pytest.mark.parametrize(
    "secret_name, secret_data, status_code, expected_result",
    [
        (
            "hf_api_key",
            SecretUploadRequest(value="my-secret-value", description="Hugging Face API key"),
            HTTPStatus.CREATED,
            True,
        ),
        (
            "deepseek_api_key",
            SecretUploadRequest(value="another-secret-value", description="DeepSeek API key"),
            HTTPStatus.NO_CONTENT,
            True,
        ),
    ],
)
def test_upload_secret(lumi_client, request_mock, secret_name, secret_data, status_code, expected_result):
    # Mocking the PUT request to upload a secret
    request_mock.put(
        url=lumi_client.client._api_url + f"/settings/secrets/{secret_name}",
        status_code=status_code,
        json={"name": secret_name, "description": secret_data.description},
    )

    result = lumi_client.settings.secrets.upload_secret(secret_name, secret_data)
    assert result == expected_result


@pytest.mark.parametrize(
    "api_key, secret_value, status_code, expected_result",
    [
        (Secrets.APIKey.HF, "my-api-key-value", HTTPStatus.CREATED, True),
        (Secrets.APIKey.MISTRAL, "another-api-key-value", HTTPStatus.NO_CONTENT, True),
    ],
)
def test_upload_api_key(lumi_client, request_mock, api_key, secret_value, status_code, expected_result):
    # Mocking the PUT request to upload an API key
    request_mock.put(
        url=lumi_client.client._api_url + f"/settings/secrets/{api_key.name}",
        status_code=status_code,
        json={"name": api_key.name, "description": api_key.description},
    )

    result = lumi_client.settings.secrets.upload_api_key(api_key, secret_value)
    assert result == expected_result


@pytest.mark.parametrize(
    "secret_name, status_code, expected_result",
    [
        ("hf_api_key", HTTPStatus.NO_CONTENT, True),
        ("deepseek_api_key", HTTPStatus.NO_CONTENT, True),
    ],
)
def test_delete_secret(lumi_client, request_mock, secret_name, status_code, expected_result):
    # Mocking the DELETE request to delete a secret
    request_mock.delete(
        url=lumi_client.client._api_url + f"/settings/secrets/{secret_name}",
        status_code=status_code,
    )

    result = lumi_client.settings.secrets.delete_secret(secret_name)
    assert result == expected_result


@pytest.mark.parametrize(
    "api_key, status_code, expected_result",
    [
        (Secrets.APIKey.HF, HTTPStatus.NO_CONTENT, True),
        (Secrets.APIKey.MISTRAL, HTTPStatus.NO_CONTENT, True),
    ],
)
def test_delete_api_key(lumi_client, request_mock, api_key, status_code, expected_result):
    # Mocking the DELETE request to delete an API key
    request_mock.delete(
        url=lumi_client.client._api_url + f"/settings/secrets/{api_key.name}",
        status_code=status_code,
    )

    result = lumi_client.settings.secrets.delete_api_key(api_key)
    assert result == expected_result
