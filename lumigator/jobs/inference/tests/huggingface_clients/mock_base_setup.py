from unittest.mock import MagicMock, patch

import pytest
from inference.schemas import GenerationConfig
from transformers import Pipeline, PreTrainedTokenizer

from schemas import PredictionResult


class MockBaseSetup:
    """Base setup for mock configurations and common test functions."""

    @pytest.fixture
    def mock_model_instance(self):
        """Create a mock model instance with standard attributes."""
        mock_model = MagicMock()
        mock_model.config.max_position_embeddings = 512
        return mock_model

    @pytest.fixture
    def mock_tokenizer_instance(self):
        """Create a mock tokenizer instance with standard attributes."""
        mock_tokenizer = MagicMock(spec=PreTrainedTokenizer)
        mock_tokenizer.model_max_length = 512
        return mock_tokenizer

    @pytest.fixture
    def mock_pipeline_instance(self, mock_model_instance, mock_tokenizer_instance):
        """Create a mock pipeline instance with model and tokenizer attributes."""
        mock_pipeline = MagicMock(spec=Pipeline)
        mock_pipeline.model = mock_model_instance
        mock_pipeline.tokenizer = mock_tokenizer_instance
        return mock_pipeline

    @pytest.fixture
    def mock_generation_config(self):
        """Create a mock generation config with standard attributes."""
        config = MagicMock(spec=GenerationConfig)
        config.max_new_tokens = 100
        return config

    @pytest.fixture
    def setup_mocks_for_seq2seq(self, mock_model_instance, mock_tokenizer_instance, mock_pipeline_instance):
        """Setup common mocks for seq2seq models."""
        with (
            patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.AutoModelForSeq2SeqLM") as mock_automodel,
            patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.AutoTokenizer") as mock_tokenizer,
            patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.pipeline") as mock_pipeline,
        ):
            mock_automodel.from_pretrained.return_value = mock_model_instance
            mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
            mock_pipeline.return_value = mock_pipeline_instance

            yield mock_pipeline, mock_automodel, mock_tokenizer
