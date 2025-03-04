from unittest.mock import MagicMock, patch

import pytest
from inference_config import InferenceJobConfig
from litellm import APIError
from model_clients import LiteLLMModelClient, PredictionResult


class TestLiteLLMModelClient:
    @pytest.fixture
    def mock_config(self):
        """Create a mock InferenceJobConfig for testing."""
        config = MagicMock(spec=InferenceJobConfig)

        # Create nested mocks for the attributes
        config.system_prompt = "You are a helpful assistant."

        # Create generation_config as a separate mock
        generation_config = MagicMock()
        generation_config.max_new_tokens = 100
        generation_config.frequency_penalty = 0.0
        generation_config.temperature = 0.7
        generation_config.top_p = 1.0
        config.generation_config = generation_config

        # Create inference_server as a separate mock
        inference_server = MagicMock()
        inference_server.provider = "openai"
        inference_server.model = "gpt-3.5-turbo"
        inference_server.base_url = "https://api.openai.com/v1"
        config.inference_server = inference_server

        return config

    @pytest.fixture
    def client(self, mock_config):
        """Create a LiteLLMModelClient instance for testing."""
        return LiteLLMModelClient(mock_config)

    @patch("model_clients.completion")
    def test_initialization(self, mock_completion, mock_config):
        """Test that the LiteLLMModelClient initializes correctly."""
        client = LiteLLMModelClient(mock_config)
        assert client.config == mock_config
        assert client.system_prompt == mock_config.system_prompt

    @patch("model_clients.completion")
    def test_predict_standard_response(self, mock_completion, client):
        """Test that predict returns the correct PredictionResult for a standard response."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response._hidden_params = {"response_cost": 0.001}
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is a test response."
        mock_response.choices[0].message.provider_specific_fields = {}
        mock_response["usage"].prompt_tokens = 10
        mock_response["usage"].completion_tokens = 5
        mock_response["usage"].total_tokens = 15
        mock_completion.return_value = mock_response

        # Call function
        result = client.predict("Test prompt")

        # Verify results
        assert isinstance(result, PredictionResult)
        assert result.prediction == "This is a test response."
        assert result.reasoning is None
        assert result.metrics.prompt_tokens == 10
        assert result.metrics.completion_tokens == 5
        assert result.metrics.total_tokens == 15
        assert result.metrics.reasoning_tokens == 0
        assert result.metrics.answer_tokens == 5

        # Verify completion was called correctly
        mock_completion.assert_called_once_with(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Test prompt"},
            ],
            max_tokens=100,
            frequency_penalty=0.0,
            temperature=0.7,
            top_p=1.0,
            drop_params=True,
            api_base="https://api.openai.com/v1",
        )

    @patch("model_clients.completion")
    def test_predict_with_reasoning_field(self, mock_completion, client):
        """Test that predict extracts reasoning from provider_specific_fields."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response._hidden_params = {"response_cost": 0.002}
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Final answer"
        mock_response.choices[0].message.provider_specific_fields = {"reasoning_content": "This is the reasoning"}
        mock_response.choices[0].message.reasoning_content = "This is the reasoning"  # Some APIs provide it directly
        mock_response["usage"].prompt_tokens = 15
        mock_response["usage"].completion_tokens = 20
        mock_response["usage"].total_tokens = 35
        mock_response["usage"]["completion_tokens_details"].reasoning_tokens = 10

        # This is the key part that needs to be fixed:
        # Set up completion_tokens_details correctly with a MagicMock that will return
        # the correct number when .reasoning_tokens is accessed
        completion_tokens_details = MagicMock()
        completion_tokens_details.reasoning_tokens = 10
        mock_response["usage"].completion_tokens_details = completion_tokens_details

        mock_completion.return_value = mock_response

        # Call function
        result = client.predict("Test prompt with reasoning")

        # Verify results
        assert result.prediction == "Final answer"
        assert result.reasoning == "This is the reasoning"
        assert result.metrics.reasoning_tokens == 10
        assert result.metrics.answer_tokens == 10  # 20 completion - 10 reasoning

    @patch("model_clients.completion")
    def test_predict_with_think_tag(self, mock_completion, client):
        """Test that predict extracts reasoning from text with </think> tag."""
        # Setup mock response with reasoning in the content
        mock_response = MagicMock()
        mock_response._hidden_params = {"response_cost": 0.003}
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = "Let me think about this.\nThis is my reasoning.\n</think>Final answer"
        mock_response.choices[0].message.provider_specific_fields = {}
        mock_response["usage"].prompt_tokens = 5
        mock_response["usage"].completion_tokens = 15
        mock_response["usage"].total_tokens = 20
        mock_completion.return_value = mock_response

        # Call function
        result = client.predict("Test prompt with think tag")

        # Verify results
        assert result.prediction == "Final answer"
        assert result.reasoning == "Let me think about this.\nThis is my reasoning."
        # Verify reasoning tokens are estimated based on word count
        assert result.metrics.reasoning_tokens > 0

    @patch("model_clients.completion")
    def test_retry_mechanism(self, mock_completion, client):
        """Test that the retry mechanism works when API calls fail."""
        # Make completion fail twice then succeed
        mock_completion.side_effect = [
            APIError(message="API Error", llm_provider="openai", model="gpt-3.5-turbo", status_code=500),
            APIError(message="API Error", llm_provider="openai", model="gpt-3.5-turbo", status_code=500),
            MagicMock(
                _hidden_params={"response_cost": 0.001},
                choices=[MagicMock(message=MagicMock(content="Success after retry", provider_specific_fields={}))],
                **{"usage": MagicMock(prompt_tokens=5, completion_tokens=3, total_tokens=8)},
            ),
        ]

        # Call function, should succeed after retries
        result = client.predict("Test retry")

        # Verify completion was called multiple times
        assert mock_completion.call_count == 3
        assert result.prediction == "Success after retry"

    @patch("model_clients.completion")
    def test_missing_inference_server(self, mock_completion, mock_config):
        """Test behavior when inference_server.base_url is None."""
        # Set the base_url to None
        mock_config.inference_server.base_url = None

        client = LiteLLMModelClient(mock_config)

        # Setup mock response
        mock_response = MagicMock()
        mock_response._hidden_params = {"response_cost": 0.0}
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.choices[0].message.provider_specific_fields = {}
        mock_response["usage"].prompt_tokens = 5
        mock_response["usage"].completion_tokens = 2
        mock_response["usage"].total_tokens = 7
        mock_completion.return_value = mock_response

        # Call function
        result = client.predict("Test without server")

        # Verify api_base is None in the completion call
        mock_completion.assert_called_once()
        args, kwargs = mock_completion.call_args
        assert kwargs["api_base"] is None

        # Verify result
        assert result.prediction == "Response"
