from enum import Enum
from http import HTTPMethod, HTTPStatus

from lumigator_sdk.client import ApiClient
from lumigator_sdk.strict_schemas import SecretGetRequest, SecretUploadRequest


class Secrets:
    """Used to configure the Lumigator backend with sensitive user settings (secrets)
    that aren't related to deployment configuration.
    """

    SECRETS_ROUTE = "secrets"  # pragma: allowlist secret

    class APIKey(Enum):
        """Enumeration of API keys that can be configured in the Lumigator backend."""

        HF = ("hf_api_key", "Hugging Face API key")
        OPENAI = ("openai_api_key", "OpenAI API key")
        DEEPSEEK = ("deepseek_api_key", "DeepSeek API key")
        MISTRAL = ("mistral_api_key", "Mistral API key")

        @property
        def name(self) -> str:
            return self.value[0]

        @property
        def description(self) -> str:
            return self.value[1]

    def __init__(self, client: ApiClient, parent_route: str):
        """Construct a new instance of the settings class.

        Args:
            client (ApiClient): The API client to use for requests.
            parent_route (str): The parent route which should be used to form request URLs.

        Returns:
            Secrets: A new Secrets instance.
        """
        self.__client = client
        self._parent_route = parent_route

    def list_secrets(self) -> list[SecretGetRequest]:
        """Lists all API configured secret names (and descriptions) stored in Lumigator.

        :returns: A list of secrets (name and description) stored in Lumigator
        :raises ValueError: if the response data is not a list
        :raises ValidationError: if any item in the response data's list is invalid
        """
        response = self.__client.get_response(f"{self._base_secrets_route()}")
        data = response.json()
        if not isinstance(data, list):
            raise ValueError("Unexpected data structure, expected a list.")

        return [SecretGetRequest.model_validate(secret) for secret in data]

    def list_api_keys(self) -> list[SecretGetRequest]:
        """Lists all API keys configured in the Lumigator backend.

        :returns: A list of secrets (name and description) which are API keys, stored in Lumigator
        :raises ValueError: if the response data is not a list
        :raises ValidationError: if any item in the response data's list is invalid
        """
        api_key_names = {key.name for key in self.APIKey}
        return [api_keys for api_keys in self.list_secrets() if api_keys.name in api_key_names]

    def is_secret_configured(self, secret_name: str) -> bool:
        """Checks if a secret is configured in the Lumigator backend."""
        return any(secret.name == secret_name.lower() for secret in self.list_secrets())

    def is_api_key_configured(self, api_key: APIKey) -> bool:
        """Checks if an API key is configured in the Lumigator backend."""
        return self.is_secret_configured(api_key.name)

    def upload_secret(self, secret_name: str, secret_data: SecretUploadRequest) -> bool:
        """Uploads a secret for use in Lumigator."""
        # Validate the secret name.
        SecretGetRequest(name=secret_name.strip(), description=secret_data.description)

        response = self.__client.get_response(
            method=HTTPMethod.PUT,
            api_path=f"{self._base_secrets_route()}/{secret_name}",
            data=secret_data.model_dump_json(),
        )

        return response.status_code == HTTPStatus.CREATED or response.status_code == HTTPStatus.NO_CONTENT

    def upload_api_key(self, api_key: APIKey, secret_value: str) -> bool:
        """Uploads an API key for an upstream provider to the Lumigator backend."""
        secret_data = SecretUploadRequest(value=secret_value, description=api_key.description)

        return self.upload_secret(secret_name=api_key.name, secret_data=secret_data)

    def delete_secret(self, secret_name: str) -> bool:
        """Deletes a secret identified by its name."""
        response = self.__client.get_response(method="DELETE", api_path=f"{self._base_secrets_route()}/{secret_name}")

        return response.status_code == HTTPStatus.NO_CONTENT

    def delete_api_key(self, api_key: APIKey) -> bool:
        """Deletes an API key from the Lumigator backend."""
        return self.delete_secret(api_key.name)

    def _base_secrets_route(self) -> str:
        return f"{self._parent_route.rstrip('/')}/{self.SECRETS_ROUTE}"
