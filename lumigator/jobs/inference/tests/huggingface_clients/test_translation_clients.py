from unittest.mock import MagicMock, patch

import pytest
from inference_config import HfPipelineConfig, InferenceJobConfig
from lumigator_schemas.tasks import TaskDefinition, TaskType
from model_clients.huggingface_clients import (
    HuggingFaceLanguageCodeTranslationClient,
    HuggingFaceOpusMTTranslationClient,
    HuggingFacePrefixTranslationClient,
)

from schemas import PredictionResult
from tests.huggingface_clients.mock_base_setup import MockBaseSetup


class TranslationClientTestBase(MockBaseSetup):
    """Base class for testing translation clients."""

    @pytest.fixture
    def mock_translation_config(self, mock_generation_config):
        """Create a mock InferenceJobConfig for testing translation clients."""
        config = MagicMock(spec=InferenceJobConfig)
        config.task_definition = MagicMock(spec=TaskDefinition)
        config.task_definition.source_language = "en"
        config.task_definition.target_language = "fr"

        config.hf_pipeline = MagicMock(spec=HfPipelineConfig)
        config.hf_pipeline.model_name_or_path = "mock-translation-model"
        config.hf_pipeline.task = TaskType.TRANSLATION
        config.hf_pipeline.trust_remote_code = False
        config.hf_pipeline.use_fast = True
        config.hf_pipeline.torch_dtype = "float32"
        config.hf_pipeline.revision = "main"
        config.hf_pipeline.device = "cpu"

        config.generation_config = mock_generation_config
        return config

    @pytest.fixture
    def mock_translation_results(self):
        """Mock translation results returned by pipeline."""
        return [
            {"translation_text": "Bonjour, comment ça va?"},
            {"translation_text": "Je suis un modèle de traduction."},
        ]

    @pytest.fixture
    def setup_translation_mocks(self, setup_mocks_for_seq2seq, mock_pipeline_instance, mock_translation_results):
        """Setup mocks specific for translation clients."""
        mock_pipeline, mock_automodel, mock_tokenizer = setup_mocks_for_seq2seq

        # Setup language resolution
        with patch("model_clients.translation_utils.resolve_user_input_language") as mock_resolve_lang:
            mock_resolve_lang.side_effect = [
                {"iso_code": "en", "full_name": "English", "alpha3_code": "eng"},
                {"iso_code": "fr", "full_name": "French", "alpha3_code": "fra"},
            ]

            mock_pipeline_instance.return_value = mock_translation_results

            yield mock_pipeline, mock_automodel, mock_tokenizer, mock_resolve_lang


class TestHuggingFacePrefixTranslationClient(TranslationClientTestBase):
    def test_initialization(self, setup_translation_mocks, mock_translation_config):
        """Test initialization of the prefix translation client."""
        mock_pipeline = setup_translation_mocks[0]

        # Initialize client
        client = HuggingFacePrefixTranslationClient(mock_translation_config)

        # Check that correct language parameters are set
        assert client.source_language_iso_code == "en"
        assert client.source_language == "English"
        assert client.target_language_iso_code == "fr"
        assert client.target_language == "French"
        assert client.prefix == "translate English to French: "

        # Verify pipeline was initialized with the correct task
        pipeline_args = mock_pipeline.call_args[1]
        assert pipeline_args["task"] == "translation_en_to_fr"

    def test_predict(self, setup_translation_mocks, mock_translation_config, mock_pipeline_instance):
        """Test the predict method of the prefix translation client."""
        # Initialize client and call predict
        client = HuggingFacePrefixTranslationClient(mock_translation_config)
        result = client.predict(["Hello, how are you?", "I am a translation model."])

        # Verify prediction
        assert len(result) == 2
        assert all(isinstance(r, PredictionResult) for r in result)
        assert result[0].prediction == "Bonjour, comment ça va?"
        assert result[1].prediction == "Je suis un modèle de traduction."

        # Verify pipeline was called with prefixed inputs
        expected_prefixed_inputs = [
            "translate English to French: Hello, how are you?",
            "translate English to French: I am a translation model.",
        ]
        mock_pipeline_instance.assert_called_once_with(expected_prefixed_inputs, max_new_tokens=100, truncation=True)


class TestHuggingFaceLanguageCodeTranslationClient(TranslationClientTestBase):
    def test_initialization(self, setup_translation_mocks, mock_translation_config):
        """Test initialization of the language code translation client."""
        mock_pipeline = setup_translation_mocks[0]

        # Initialize client
        client = HuggingFaceLanguageCodeTranslationClient(mock_translation_config)

        # Check that correct language parameters are set
        assert client.source_language_iso_code == "en"
        assert client.source_language == "English"
        assert client.target_language_iso_code == "fr"
        assert client.target_language == "French"

        # Verify pipeline task is correctly set for translation
        pipeline_args = mock_pipeline.call_args[1]
        assert pipeline_args["task"] == TaskType.TRANSLATION

    def test_predict(self, setup_translation_mocks, mock_translation_config, mock_pipeline_instance):
        """Test the predict method of the language code translation client."""
        # Initialize client and call predict
        client = HuggingFaceLanguageCodeTranslationClient(mock_translation_config)
        result = client.predict(["Hello, how are you?", "I am a translation model."])

        # Verify prediction
        assert len(result) == 2
        assert all(isinstance(r, PredictionResult) for r in result)
        assert result[0].prediction == "Bonjour, comment ça va?"
        assert result[1].prediction == "Je suis un modèle de traduction."

        # Verify pipeline was called with correct language codes
        mock_pipeline_instance.assert_called_once_with(
            ["Hello, how are you?", "I am a translation model."],
            max_new_tokens=100,
            truncation=True,
            src_lang="en",
            tgt_lang="fr",
        )


class TestHuggingFaceOpusMTTranslationClient(TranslationClientTestBase):
    def test_initialize(self, setup_translation_mocks, mock_translation_config):
        """Test the initialization of the Opus MT translation client."""
        mock_pipeline = setup_translation_mocks[0]

        with patch("model_clients.translation_utils.resolve_user_input_language") as mock_resolve_lang:
            mock_resolve_lang.side_effect = [
                {"iso_code": "en", "full_name": "English", "alpha3_code": "eng"},
                {"iso_code": "fr", "full_name": "French", "alpha3_code": "fra"},
            ]
            # Initialize client
            client = HuggingFaceOpusMTTranslationClient(mock_translation_config)

            # Verify target language prefix string is set correctly
            assert client.target_language_prefix_string == ">>fra<< "

            # Verify pipeline task is correctly set for translation
            pipeline_args = mock_pipeline.call_args[1]
            assert pipeline_args["task"] == TaskType.TRANSLATION
