from unittest.mock import MagicMock, patch

import pytest
from inference_config import InferenceJobConfig
from lumigator_schemas.tasks import TaskType
from model_clients.huggingface_clients import (
    HuggingFaceCausalLMClient,
    HuggingFaceSeq2SeqSummarizationClient,
)

from schemas import PredictionResult


class TestHuggingFaceSeq2SeqSummarizationClient:
    @pytest.fixture
    def mock_config(self):
        """Create a mock InferenceJobConfig for testing seq2seq client."""
        config = MagicMock(spec=InferenceJobConfig)
        config.hf_pipeline = MagicMock()
        config.hf_pipeline.model_name_or_path = "mock-seq2seq-model"
        config.hf_pipeline.task = TaskType.SUMMARIZATION
        config.hf_pipeline.use_fast = True
        config.hf_pipeline.trust_remote_code = False
        config.hf_pipeline.torch_dtype = "float32"
        config.hf_pipeline.revision = "main"
        config.hf_pipeline.device = "cpu"

        config.generation_config = MagicMock()
        config.generation_config.max_new_tokens = 100

        return config

    @patch("model_clients.huggingface_clients.AutoTokenizer")
    @patch("model_clients.huggingface_clients.AutoModelForSeq2SeqLM")
    @patch("model_clients.huggingface_clients.pipeline")
    def test_initialization(self, mock_pipeline, mock_automodel, mock_tokenizer, mock_config):
        """Test initialization of the seq2seq client."""
        # Setup mocks
        mock_model = MagicMock()
        mock_model.config.max_position_embeddings = 512
        mock_automodel.from_pretrained.return_value = mock_model

        mock_tokenizer_instance = MagicMock()
        mock_tokenizer_instance.model_max_length = 512
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance

        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.model = mock_model
        mock_pipeline_instance.tokenizer = mock_tokenizer_instance
        mock_pipeline.return_value = mock_pipeline_instance

        # Initialize client
        client = HuggingFaceSeq2SeqSummarizationClient(mock_config)

        # Verify initialization
        mock_tokenizer.from_pretrained.assert_called_once()
        mock_automodel.from_pretrained.assert_called_once()
        mock_pipeline.assert_called_once()
        assert client._pipeline == mock_pipeline_instance

    @patch("model_clients.huggingface_clients.AutoTokenizer")
    @patch("model_clients.huggingface_clients.AutoModelForSeq2SeqLM")
    @patch("model_clients.huggingface_clients.pipeline")
    def test_predict(self, mock_pipeline, mock_automodel, mock_tokenizer, mock_config):
        """Test the predict method of the seq2seq client."""
        # Setup mocks
        mock_model = MagicMock()
        mock_model.config.max_position_embeddings = 512
        mock_automodel.from_pretrained.return_value = mock_model

        mock_tokenizer_instance = MagicMock()
        mock_tokenizer_instance.model_max_length = 512
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance

        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.model = mock_model
        mock_pipeline_instance.tokenizer = mock_tokenizer_instance
        mock_pipeline_instance.return_value = [{"summary_text": "This is a summary."}]
        mock_pipeline.return_value = mock_pipeline_instance

        # Initialize client and call predict
        client = HuggingFaceSeq2SeqSummarizationClient(mock_config)
        result = client.predict("This is a test prompt.")

        # Verify prediction
        assert isinstance(result, PredictionResult)
        assert result.prediction == "This is a summary."
        mock_pipeline_instance.assert_called_once_with("This is a test prompt.", max_new_tokens=100, truncation=True)

    @patch("model_clients.huggingface_clients.AutoTokenizer")
    @patch("model_clients.huggingface_clients.AutoModelForSeq2SeqLM")
    @patch("model_clients.huggingface_clients.pipeline")
    def test_max_token_adjustment(self, mock_pipeline, mock_automodel, mock_tokenizer, mock_config):
        """Test that the client adjusts max tokens if over model limits."""
        # Setup mocks with limited max position embeddings
        mock_model = MagicMock()
        mock_model.config.max_position_embeddings = 50  # Lower than config.max_new_tokens
        mock_automodel.from_pretrained.return_value = mock_model

        mock_tokenizer_instance = MagicMock()
        mock_tokenizer_instance.model_max_length = 512
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance

        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.model = mock_model
        mock_pipeline_instance.tokenizer = mock_tokenizer_instance
        mock_pipeline.return_value = mock_pipeline_instance

        # Set the initial max_new_tokens to a value higher than model's max_position_embeddings
        mock_config.generation_config.max_new_tokens = 100
        # Initialize client - which should trigger the token adjustment
        client = HuggingFaceSeq2SeqSummarizationClient(mock_config)
        # Verify the max_new_tokens was adjusted down to the model's max_position_embeddings
        assert client._config.generation_config.max_new_tokens == 50

        # Now test with a value that's already within limits
        mock_config.generation_config.max_new_tokens = 30  # Less than max_position_embeddings
        # Initialize a new client
        client = HuggingFaceSeq2SeqSummarizationClient(mock_config)
        # Verify max_new_tokens was NOT adjusted since it was already within limits
        assert client._config.generation_config.max_new_tokens == 30


class TestHuggingFaceCausalLMClient:
    @pytest.fixture
    def mock_config(self):
        """Create a mock InferenceJobConfig for testing causal LM client."""
        config = MagicMock(spec=InferenceJobConfig)
        config.hf_pipeline = MagicMock()
        config.hf_pipeline.model_name_or_path = "mock-causal-model"
        config.hf_pipeline.task = TaskType.TEXT_GENERATION
        config.hf_pipeline.model_dump.return_value = {
            "model_name_or_path": "mock-causal-model",
            "task": TaskType.TEXT_GENERATION,
        }

        config.system_prompt = "You are a helpful assistant."
        config.generation_config = MagicMock()
        config.generation_config.max_new_tokens = 100

        return config

    @patch("model_clients.huggingface_clients.pipeline")
    def test_initialization(self, mock_pipeline, mock_config):
        """Test initialization of the causal LM client."""
        # Setup mocks
        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance

        # Initialize client
        client = HuggingFaceCausalLMClient(mock_config)

        # Verify initialization
        mock_pipeline.assert_called_once()
        assert client._pipeline == mock_pipeline_instance
        assert client._system_prompt == "You are a helpful assistant."

    @patch("model_clients.huggingface_clients.pipeline")
    def test_with_summarization_task(self, mock_pipeline, mock_config):
        """Test the causal LM client with a summarization task through system prompt."""
        # Set task to summarization and use appropriate system prompt
        mock_config.hf_pipeline.task = TaskType.SUMMARIZATION
        mock_config.system_prompt = "Summarize the following text."

        # Ensure pipeline config is still set to text-generation (overridden in client init)
        mock_config.hf_pipeline.model_dump.return_value = {
            "model_name_or_path": "mock-causal-model",
            "task": TaskType.TEXT_GENERATION,  # Should still be text-generation in dumped config
        }

        # Setup mock pipeline response
        mock_response = [
            {
                "generated_text": [
                    {"role": "system", "content": "Summarize the following text."},
                    {"role": "user", "content": "Long article about climate change..."},
                    {"role": "assistant", "content": "Climate change is affecting the planet in various ways."},
                ]
            }
        ]
        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.return_value = mock_response
        mock_pipeline.return_value = mock_pipeline_instance

        # Initialize client and call predict
        client = HuggingFaceCausalLMClient(mock_config)
        result = client.predict("Long article about climate change...")

        # Verify prediction
        assert isinstance(result, PredictionResult)
        assert result.prediction == "Climate change is affecting the planet in various ways."

        # Verify pipeline task was correctly overridden to text-generation
        mock_pipeline.assert_called_once()
        pipeline_args = mock_pipeline.call_args[1]
        assert pipeline_args["task"] == TaskType.TEXT_GENERATION
