from pathlib import Path

import yaml
from langcodes import Language, find, tag_is_valid
from langcodes.tag_parser import LanguageTagError


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


def is_valid_language_tag(language_str: str) -> bool:
    """Check if the string is a valid language tag.

    Example:
        is_valid_language_tag("en-US") -> True
        is_valid_language_tag("English") -> False

    Args:
        language_str: A string that might be a language tag

    Returns:
        True if the string is a valid language tag, False otherwise
    """
    try:
        normalized = language_str.replace("_", "-")
        return tag_is_valid(normalized)
    except LanguageTagError:
        return False


def get_language_from_tag(language_tag: str) -> Language | None:
    """Convert a language tag to a Language object.

    Example:
        get_language_from_tag("de-AT") -> Language object for German (Austria)
        get_language_from_tag("xyz") -> None (invalid tag)

    Args:
        language_tag: A string containing a language tag

    Returns:
        Language object if valid, None otherwise
    """
    try:
        normalized = language_tag.replace("_", "-")
        return Language.get(normalized)
    except LanguageTagError:
        return None


def get_language_from_name(language_name: str) -> Language | None:
    """Convert a language name to a Language object.

    Example:
        get_language_from_name("German") -> Language object for German
        get_language_from_name("NonExistentLanguage") -> None

    Args:
        language_name: A string containing a language name

    Returns:
        Language object if valid, None otherwise
    """
    try:
        return find(language_name)
    except (LookupError, ValueError):
        return None


def extract_language_info(lang: Language | None) -> dict[str, str] | None:
    """Extract standardized information from a Language object.

    Example:
        extract_language_info(Language.get("fr")) ->
        {"iso_code": "fr", "full_name": "French"}

    Args:
        lang: A Language object

    Returns:
        Dictionary with language information or None if input is None
    """
    if not lang:
        return None

    return {"iso_code": lang.language, "full_name": lang.display_name()}


def resolve_user_input_language(language_str: str) -> dict[str, str]:
    """Determine if the input is a language code or display name and extract information.

    Example:
        resolve_user_input_language("de") ->
        {"type": "code", "iso_code": "de", "full_name": "German"}

        resolve_user_input_language("French") ->
        {"type": "display_name", "iso_code": "fr", "full_name": "French"}

    Args:
        language_str: A string that might be a language code or name

    Returns:
        Dictionary with language type and information

    Raises:
        ValueError: If the language string cannot be recognized
    """
    # First try as a language tag
    if is_valid_language_tag(language_str):
        lang = get_language_from_tag(language_str)
        if lang:
            info = extract_language_info(lang)
            return {"type": "code", **info}

    # Then try as a language name
    lang = get_language_from_name(language_str)
    if lang:
        info = extract_language_info(lang)
        return {"type": "display_name", **info}

    # If all fails
    raise ValueError(f"Unrecognized language code or name: {language_str}")
