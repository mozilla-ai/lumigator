from unittest.mock import MagicMock, patch

import pytest
from inference_config import InferenceJobConfig
from litellm import APIError
from model_clients.external_api_clients import LiteLLMModelClient, PredictionResult

# Constants
SYSTEM_PROMPT = "You are a helpful assistant."
DEFAULT_MAX_TOKENS = 100
DEFAULT_FREQ_PENALTY = 0.0
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 1.0
PROVIDER = "openai"
MODEL = "gpt-4o"
BASE_URL = "https://api.openai.com/v1"
TEST_PROMPT = [[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": "Test prompt"}]]
TEST_RESPONSE = "This is a test response."
HIDDEN_PARAMS = {"response_cost": 0.001}


class TestLiteLLMModelClient:
    @pytest.fixture
    def mock_config(self):
        """Create a mock InferenceJobConfig for testing."""
        config = MagicMock(spec=InferenceJobConfig)
        config.system_prompt = SYSTEM_PROMPT

        # Create generation_config as a separate mock
        generation_config = MagicMock()
        generation_config.max_new_tokens = DEFAULT_MAX_TOKENS
        generation_config.frequency_penalty = DEFAULT_FREQ_PENALTY
        generation_config.temperature = DEFAULT_TEMPERATURE
        generation_config.top_p = DEFAULT_TOP_P
        config.generation_config = generation_config

        # Create inference_server as a separate mock
        inference_server = MagicMock()
        inference_server.provider = PROVIDER
        inference_server.model = MODEL
        inference_server.base_url = BASE_URL
        config.inference_server = inference_server

        return config

    @pytest.fixture(scope="function")
    def client(self, mock_config):
        """Create a LiteLLMModelClient instance for testing."""
        return LiteLLMModelClient(mock_config)

    @pytest.fixture(scope="function")
    def client_with_api_key(self, mock_config, api_key):
        """Create a LiteLLMModelClient instance for testing."""
        return LiteLLMModelClient(mock_config, api_key)

    @pytest.fixture
    def mock_standard_response(self):
        """Create a standard mock response"""
        mock_response = MagicMock()
        mock_response._hidden_params = HIDDEN_PARAMS
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = TEST_RESPONSE
        mock_response.choices[0].message.provider_specific_fields = {}
        mock_response["usage"].prompt_tokens = 10
        mock_response["usage"].completion_tokens = 5
        mock_response["usage"].total_tokens = 15
        return [mock_response]

    def test_initialization(self, mock_config):
        """Test that the LiteLLMModelClient initializes correctly."""
        client = LiteLLMModelClient(mock_config)
        assert client.config == mock_config
        assert client.system_prompt == mock_config.system_prompt

    @patch("model_clients.external_api_clients.batch_completion")
    def test_predict_standard_response(self, mock_completion, client_with_api_key, mock_standard_response, api_key):
        """Test that predict returns the correct PredictionResult for a standard response."""
        # Setup mock response
        mock_completion.return_value = mock_standard_response
        # Call function
        result = client_with_api_key.predict(TEST_PROMPT)

        # Verify results
        assert isinstance(result[0], PredictionResult)
        assert result[0].prediction == TEST_RESPONSE
        assert result[0].reasoning is None
        assert result[0].metrics.prompt_tokens == 10
        assert result[0].metrics.completion_tokens == 5
        assert result[0].metrics.total_tokens == 15
        assert result[0].metrics.reasoning_tokens == 0
        assert result[0].metrics.answer_tokens == 5

        # Verify completion was called correctly
        mock_completion.assert_called_once_with(
            model=f"{PROVIDER}/{MODEL}",
            messages=TEST_PROMPT,
            max_tokens=DEFAULT_MAX_TOKENS,
            frequency_penalty=DEFAULT_FREQ_PENALTY,
            temperature=DEFAULT_TEMPERATURE,
            top_p=DEFAULT_TOP_P,
            drop_params=True,
            api_base=BASE_URL,
            api_key=api_key,
        )

    @patch("model_clients.external_api_clients.batch_completion")
    def test_predict_with_reasoning_field(self, mock_completion, client):
        """Test that predict extracts reasoning from provider_specific_fields."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response._hidden_params = HIDDEN_PARAMS
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Final answer"
        mock_response.choices[0].message.provider_specific_fields = {"reasoning_content": "This is the reasoning"}
        mock_response.choices[0].message.reasoning_content = "This is the reasoning"  # Some APIs provide it directly
        mock_response["usage"].prompt_tokens = 15
        mock_response["usage"].completion_tokens = 20
        mock_response["usage"].total_tokens = 35
        mock_response["usage"]["completion_tokens_details"].reasoning_tokens = 10

        # Set up completion_tokens_details correctly
        completion_tokens_details = MagicMock()
        completion_tokens_details.reasoning_tokens = 10
        mock_response["usage"].completion_tokens_details = completion_tokens_details

        mock_completion.return_value = [mock_response]

        # Call function
        result = client.predict(TEST_PROMPT)

        # Verify results
        assert result[0].prediction == "Final answer"
        assert result[0].reasoning == "This is the reasoning"
        assert result[0].metrics.reasoning_tokens == 10
        assert result[0].metrics.answer_tokens == 10  # 20 completion - 10 reasoning

    @patch("model_clients.external_api_clients.batch_completion")
    def test_predict_with_think_tag(self, mock_completion, client):
        """Test that predict extracts reasoning from text with </think> tag."""
        # Setup mock response with reasoning in the content
        mock_response = MagicMock()
        mock_response._hidden_params = HIDDEN_PARAMS
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = "Let me think about this.\nThis is my reasoning.\n</think>Final answer"
        mock_response.choices[0].message.provider_specific_fields = {}
        mock_response["usage"].prompt_tokens = 5
        mock_response["usage"].completion_tokens = 15
        mock_response["usage"].total_tokens = 20
        mock_completion.return_value = [mock_response]

        # Call function
        result = client.predict(TEST_PROMPT)

        # Verify results
        assert result[0].prediction == "Final answer"
        assert result[0].reasoning == "Let me think about this.\nThis is my reasoning."
        # Verify reasoning tokens are estimated based on word count
        assert result[0].metrics.reasoning_tokens > 0

    @patch("model_clients.external_api_clients.batch_completion")
    def test_retry_mechanism(self, mock_completion, client):
        """Test that the retry mechanism works when API calls fail."""
        # Create API errors for the first two attempts
        api_error = APIError(message="API Error", llm_provider=PROVIDER, model=MODEL, status_code=500)

        # Configure success on third try
        success_response = MagicMock()
        success_response._hidden_params = HIDDEN_PARAMS
        success_response.choices = [MagicMock()]
        success_response.choices[0].message.content = "Success after retry"
        success_response.choices[0].message.provider_specific_fields = {}
        success_response["usage"].prompt_tokens = 5
        success_response["usage"].completion_tokens = 3
        success_response["usage"].total_tokens = 8

        # Make completion fail twice then succeed
        mock_completion.side_effect = [api_error, api_error, [success_response]]

        # Call function, should succeed after retries
        result = client.predict(TEST_PROMPT)

        # Verify completion was called multiple times
        assert mock_completion.call_count == 3
        assert result[0].prediction == "Success after retry"

    @patch("model_clients.external_api_clients.batch_completion")
    def test_missing_inference_server(self, mock_completion, mock_config):
        """Test behavior when inference_server.base_url is None."""
        # Set the base_url to None
        mock_config.inference_server.base_url = None

        client = LiteLLMModelClient(mock_config)

        # Setup mock response
        mock_response = MagicMock()
        mock_response._hidden_params = HIDDEN_PARAMS
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.choices[0].message.provider_specific_fields = {}
        mock_response["usage"].prompt_tokens = 5
        mock_response["usage"].completion_tokens = 2
        mock_response["usage"].total_tokens = 7
        mock_completion.return_value = [mock_response]

        # Call function
        result = client.predict(TEST_PROMPT)

        # Verify api_base is None in the completion call
        mock_completion.assert_called_once()
        args, kwargs = mock_completion.call_args
        assert kwargs["api_base"] is None

        # Verify result
        assert result[0].prediction == "Response"
