from pathlib import Path

import yaml


def load_translation_config():
    """Load the translation models configuration from YAML file"""
    try:
        # Get the current file's directory and construct path to config file
        current_file = Path(__file__).resolve()
        config_path = current_file.parent / "translation_models.yaml"

        # Open and load the yaml file
        with config_path.open() as file:
            translation_config = yaml.safe_load(file)

        return translation_config
    except Exception as e:
        raise Exception("Error loading translation models configuration.") from e
