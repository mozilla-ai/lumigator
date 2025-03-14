from unittest.mock import MagicMock, patch

import pytest
from inference_config import HfPipelineConfig, InferenceJobConfig
from lumigator_schemas.tasks import TaskType
from model_clients.huggingface_clients import HuggingFaceSeq2SeqSummarizationClient

from schemas import PredictionResult
from tests.huggingface_clients.mock_base_setup import MockBaseSetup


class TestHuggingFaceSeq2SeqSummarizationClient(MockBaseSetup):
    @pytest.fixture
    def mock_config(self, mock_generation_config):
        """Create a mock InferenceJobConfig for testing seq2seq client."""
        config = MagicMock(spec=InferenceJobConfig)

        # Mock the HfPipelineConfig instead of creating a real instance
        config.hf_pipeline = MagicMock(spec=HfPipelineConfig)
        config.hf_pipeline.model_name_or_path = "mock-seq2seq-model"
        config.hf_pipeline.task = TaskType.SUMMARIZATION
        config.hf_pipeline.use_fast = True
        config.hf_pipeline.trust_remote_code = False
        config.hf_pipeline.torch_dtype = "float32"
        config.hf_pipeline.revision = "main"
        config.hf_pipeline.device = "cpu"

        config.generation_config = mock_generation_config

        return config

    def test_initialization(self, setup_mocks_for_seq2seq, mock_config):
        """Test initialization of the seq2seq client."""
        mock_pipeline, mock_automodel, mock_tokenizer = setup_mocks_for_seq2seq

        # Initialize client with API key
        api_key = "test-api-key"  # pragma: allowlist secret
        client = HuggingFaceSeq2SeqSummarizationClient(mock_config, api_key)

        # Verify initialization of model and tokenizer (using more flexible assertions)
        mock_automodel.from_pretrained.assert_called_once()
        model_call_args, model_call_kwargs = mock_automodel.from_pretrained.call_args
        assert model_call_args[0] == mock_config.hf_pipeline.model_name_or_path

        mock_tokenizer.from_pretrained.assert_called_once()
        tokenizer_call_args, tokenizer_call_kwargs = mock_tokenizer.from_pretrained.call_args
        assert tokenizer_call_args[0] == mock_config.hf_pipeline.model_name_or_path

        # Verify pipeline initialization
        mock_pipeline.assert_called_once()
        pipeline_args, pipeline_kwargs = mock_pipeline.call_args
        assert pipeline_kwargs["task"] == TaskType.SUMMARIZATION
        assert pipeline_kwargs["model"] == client.model
        assert pipeline_kwargs["tokenizer"] == client.tokenizer
        assert pipeline_kwargs["token"] == api_key

        # Verify client attributes
        assert client.api_key == api_key
        assert client.model is not None
        assert client.tokenizer is not None
        assert client.pipeline is not None

    def test_predict(self, setup_mocks_for_seq2seq, mock_config, mock_pipeline_instance):
        """Test the predict method of the seq2seq client."""
        mock_pipeline_instance.return_value = [{"summary_text": "This is a summary."}]

        # Note: We're NOT replacing the pipeline itself, just configuring what it returns when called

        # Initialize client and call predict
        client = HuggingFaceSeq2SeqSummarizationClient(mock_config)
        result = client.predict(["This is a test prompt."])

        # Verify prediction
        assert isinstance(result[0], PredictionResult)
        assert result[0].prediction == "This is a summary."
        mock_pipeline_instance.assert_called_once_with(["This is a test prompt."], max_new_tokens=100, truncation=True)

    def test_max_token_adjustment(self, setup_mocks_for_seq2seq, mock_config, mock_model_instance):
        """Test that the client adjusts max tokens if over model limits."""
        # Set model to have limited max position embeddings
        mock_model_instance.config.max_position_embeddings = 50  # Lower than config.max_new_tokens

        # Test token adjustment: config value higher than model limit
        mock_config.generation_config.max_new_tokens = 100
        client = HuggingFaceSeq2SeqSummarizationClient(mock_config)
        assert client.config.generation_config.max_new_tokens == 50

        # Test no adjustment needed: config value within model limit
        mock_config.generation_config.max_new_tokens = 30
        client = HuggingFaceSeq2SeqSummarizationClient(mock_config)
        assert client.config.generation_config.max_new_tokens == 30
