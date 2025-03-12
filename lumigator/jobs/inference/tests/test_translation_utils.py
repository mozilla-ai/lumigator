import pytest
from langcodes import Language
from model_clients.translation_utils import (
    extract_language_info,
    get_language_from_name,
    get_language_from_tag,
    is_valid_language_tag,
    resolve_user_input_language,
)


def test_is_valid_language_tag():
    # Valid tags
    assert is_valid_language_tag("en") and is_valid_language_tag("en-US") and is_valid_language_tag("en_GB")
    # Invalid tags
    assert not is_valid_language_tag("English") and not is_valid_language_tag("123") and not is_valid_language_tag("")


def test_get_language_from_tag():
    # Valid tags
    en_lang = get_language_from_tag("en")
    assert isinstance(en_lang, Language) and en_lang.language == "en"
    # Invalid tags
    assert get_language_from_tag("English") is None and get_language_from_tag("") is None


def test_get_language_from_name():
    # Valid names
    assert get_language_from_name("English").language == "en"
    assert get_language_from_name("german").language == "de"  # Case insensitivity
    # Invalid names
    assert get_language_from_name("NonExistentLanguage") is None


def test_extract_language_info():
    assert extract_language_info(Language.get("en")) == {"iso_code": "en", "full_name": "English"}
    assert extract_language_info(None) is None


def test_resolve_user_input_language():
    # Language codes
    en_result = resolve_user_input_language("en")
    assert en_result["type"] == "code" and en_result["iso_code"] == "en"
    # Language names
    fr_result = resolve_user_input_language("French")
    assert fr_result["type"] == "display_name" and fr_result["iso_code"] == "fr"

    # Invalid input
    with pytest.raises(ValueError, match="Unrecognized language code or name"):
        resolve_user_input_language("NonExistentLanguage")
