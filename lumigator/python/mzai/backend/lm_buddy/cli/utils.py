from pathlib import Path
from typing import TypeVar

from lm_buddy.configs.jobs.common import JobConfig

ConfigType = TypeVar("ConfigType", bound=JobConfig)


def parse_config_option(config_cls: type[ConfigType], config: str) -> ConfigType:
    """Parse the config option string from the CLI.

    If it corresponds to a path that exists, attempt to load the config from YAML file.
    If not, attempt to parse it as a JSON string.
    """
    if Path(config).exists():
        return config_cls.from_yaml_file(config)
    else:
        return config_cls.model_validate_json(config)
