from unittest.mock import MagicMock, patch

import pytest
from lumigator_schemas.tasks import TaskDefinition
from model_clients.mixins.language_code_mixin import LanguageCodesSetupMixin


class TestLanguageCodesSetupMixin:
    @pytest.fixture
    def language_mixin(self):
        """Return a simple instance of the LanguageCodesSetupMixin."""
        return LanguageCodesSetupMixin()

    @patch("model_clients.mixins.language_code_mixin.resolve_user_input_language")
    def test_setup_translation_languages_success(self, mock_resolve, language_mixin):
        """Test successful setup of source and target languages."""
        # Setup mock task definition with source and target languages
        task_def = MagicMock(spec=TaskDefinition)
        task_def.source_language = "english"
        task_def.target_language = "french"

        # Mock the resolve_user_input_language function
        mock_resolve.side_effect = [
            {"iso_code": "en", "full_name": "English"},
            {"iso_code": "fr", "full_name": "French"},
        ]

        # Call the method
        language_mixin.setup_translation_languages(task_def)

        # Verify the attributes were set correctly
        assert language_mixin.source_language_iso_code == "en"
        assert language_mixin.source_language == "English"
        assert language_mixin.target_language_iso_code == "fr"
        assert language_mixin.target_language == "French"

        # Verify resolve_user_input_language was called twice with correct arguments
        assert mock_resolve.call_count == 2
        mock_resolve.assert_any_call("english")
        mock_resolve.assert_any_call("french")

    @patch("model_clients.mixins.language_code_mixin.resolve_user_input_language")
    def test_setup_translation_languages_with_iso_codes(self, mock_resolve, language_mixin):
        """Test setup with ISO codes instead of full language names."""
        # Setup mock task definition with ISO code languages
        task_def = MagicMock(spec=TaskDefinition)
        task_def.source_language = "en"
        task_def.target_language = "fr"

        # Mock the resolve_user_input_language function
        mock_resolve.side_effect = [
            {"iso_code": "en", "full_name": "English"},
            {"iso_code": "fr", "full_name": "French"},
        ]

        # Call the method
        language_mixin.setup_translation_languages(task_def)

        # Verify the attributes were set correctly
        assert language_mixin.source_language_iso_code == "en"
        assert language_mixin.source_language == "English"
        assert language_mixin.target_language_iso_code == "fr"
        assert language_mixin.target_language == "French"

        # Verify resolve_user_input_language was called with ISO codes
        mock_resolve.assert_any_call("en")
        mock_resolve.assert_any_call("fr")
