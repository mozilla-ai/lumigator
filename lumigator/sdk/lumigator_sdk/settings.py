from lumigator_sdk.client import ApiClient
from lumigator_sdk.settings_secrets import Secrets


class Settings:
    """Used to configure the Lumigator backend with user settings that aren't related to deployment configuration."""

    SETTINGS_ROUTE = "settings"

    def __init__(self, client: ApiClient):
        """Construct a new instance of the settings class.

        Args:
            client (ApiClient): The API client to use for requests.

        Returns:
            Settings: A new settings instance.
        """
        self.__client = client
        self.secrets = Secrets(client, self.SETTINGS_ROUTE)
