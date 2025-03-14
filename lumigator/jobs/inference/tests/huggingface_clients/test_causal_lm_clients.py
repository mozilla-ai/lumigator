from unittest.mock import MagicMock, patch

import pytest
from inference_config import HfPipelineConfig, InferenceJobConfig
from lumigator_schemas.tasks import TaskType
from model_clients.huggingface_clients import HuggingFaceCausalLMClient
from transformers import Pipeline

from schemas import PredictionResult
from tests.huggingface_clients.mock_base_setup import MockBaseSetup


class TestHuggingFaceCausalLMClient(MockBaseSetup):
    @pytest.fixture
    def mock_config(self, mock_generation_config):
        """Create a mock InferenceJobConfig for testing causal LM client."""
        config = MagicMock(spec=InferenceJobConfig)

        config.hf_pipeline = MagicMock(spec=HfPipelineConfig)
        config.hf_pipeline.model_name_or_path = "mock-causal-model"
        config.hf_pipeline.task = TaskType.TEXT_GENERATION
        config.system_prompt = "You are a helpful assistant."
        config.generation_config = mock_generation_config

        return config

    @patch("model_clients.huggingface_clients.pipeline")
    def test_initialization(self, mock_pipeline, mock_config, mock_pipeline_instance):
        """Test initialization of the causal LM client."""
        mock_pipeline.return_value = mock_pipeline_instance

        # Initialize client
        client = HuggingFaceCausalLMClient(mock_config)

        # Verify initialization
        mock_pipeline.assert_called_once()
        assert client.pipeline == mock_pipeline_instance
        assert client.system_prompt == "You are a helpful assistant."

    @patch("model_clients.huggingface_clients.pipeline")
    def test_with_summarization_task(self, mock_pipeline, mock_config):
        """Test the causal LM client with a summarization task through system prompt."""
        # Set task to summarization and use appropriate system prompt
        mock_config.hf_pipeline.task = TaskType.SUMMARIZATION
        mock_config.system_prompt = "Summarize the following text."

        test_prompt = [
            [
                {"role": "system", "content": mock_config.system_prompt},
                {"role": "user", "content": "Long article about climate change..."},
            ]
        ]
        # Ensure pipeline config is still set to text-generation (overridden in client init)
        mock_config.hf_pipeline.model_dump.return_value = {
            "model_name_or_path": "mock-causal-model",
            "task": TaskType.TEXT_GENERATION,  # Should still be text-generation in dumped config
        }

        # Setup mock pipeline response
        mock_response = [
            [
                {
                    "generated_text": [
                        {"role": "system", "content": "Summarize the following text."},
                        {"role": "user", "content": "Long article about climate change..."},
                        {"role": "assistant", "content": "Climate change is affecting the planet in various ways."},
                    ]
                }
            ]
        ]
        mock_pipeline_instance = MagicMock(spec=Pipeline)
        mock_pipeline_instance.return_value = mock_response
        mock_pipeline.return_value = mock_pipeline_instance

        # Initialize client and call predict
        client = HuggingFaceCausalLMClient(mock_config)
        result = client.predict(test_prompt)

        # Verify prediction
        assert isinstance(result[0], PredictionResult)
        assert result[0].prediction == "Climate change is affecting the planet in various ways."

        # Verify pipeline task was correctly overridden to text-generation
        mock_pipeline.assert_called_once()
        pipeline_args = mock_pipeline.call_args[1]
        assert pipeline_args["task"] == TaskType.TEXT_GENERATION
