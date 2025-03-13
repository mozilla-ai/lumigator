from unittest.mock import MagicMock, patch

import pytest
from inference_config import GenerationConfig, HfPipelineConfig, InferenceJobConfig
from lumigator_schemas.tasks import TaskDefinition, TaskType
from model_clients.huggingface_clients import (
    HuggingFaceCausalLMClient,
    HuggingFacePrefixTranslationClient,
    HuggingFaceSeq2SeqSummarizationClient,
)
from transformers import Pipeline, PreTrainedTokenizer

from schemas import PredictionResult

TEST_PROMPT = [
    [{"role": "system", "content": "You are a helpfull assistant."}, {"role": "user", "content": "Test prompt"}]
]


class TestHuggingFaceSeq2SeqSummarizationClient:
    @pytest.fixture
    def mock_config(self):
        """Create a mock InferenceJobConfig for testing seq2seq client."""
        config = MagicMock(spec=InferenceJobConfig)

        config.hf_pipeline = MagicMock(spec=HfPipelineConfig)
        config.hf_pipeline.model_name_or_path = "mock-seq2seq-model"
        config.hf_pipeline.task = TaskType.SUMMARIZATION
        config.hf_pipeline.use_fast = True
        config.hf_pipeline.trust_remote_code = False
        config.hf_pipeline.torch_dtype = "float32"
        config.hf_pipeline.revision = "main"
        config.hf_pipeline.device = "cpu"

        config.generation_config = MagicMock(spec=GenerationConfig)
        config.generation_config.max_new_tokens = 100

        return config

    @patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.AutoTokenizer")
    @patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.AutoModelForSeq2SeqLM")
    @patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.pipeline")
    def test_predict(self, mock_pipeline, mock_automodel, mock_tokenizer, mock_config):
        """Test the predict method of the seq2seq client."""
        # Setup mocks
        mock_model = MagicMock()
        mock_model.config.max_position_embeddings = 512
        mock_automodel.from_pretrained.return_value = mock_model

        mock_tokenizer_instance = MagicMock(spec=PreTrainedTokenizer)
        mock_tokenizer_instance.model_max_length = 512
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance

        mock_pipeline_instance = MagicMock(spec=Pipeline)
        mock_pipeline_instance.model = mock_model
        mock_pipeline_instance.tokenizer = mock_tokenizer_instance
        mock_pipeline_instance.return_value = [{"summary_text": "This is a summary."}]
        mock_pipeline.return_value = mock_pipeline_instance

        # Initialize client and call predict
        client = HuggingFaceSeq2SeqSummarizationClient(mock_config)
        result = client.predict(["This is a test prompt."])

        # Verify prediction
        assert isinstance(result[0], PredictionResult)
        assert result[0].prediction == "This is a summary."
        mock_pipeline_instance.assert_called_once_with(["This is a test prompt."], max_new_tokens=100, truncation=True)

    @patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.AutoTokenizer")
    @patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.AutoModelForSeq2SeqLM")
    @patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.pipeline")
    def test_initialization(self, mock_pipeline, mock_automodel, mock_tokenizer, mock_config, api_key):
        """Test initialization of the seq2seq client."""
        # Setup mocks
        mock_model = MagicMock()
        mock_model.config.max_position_embeddings = 512
        mock_automodel.from_pretrained.return_value = mock_model

        mock_tokenizer_instance = MagicMock(spec=PreTrainedTokenizer)
        mock_tokenizer_instance.model_max_length = 512
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance

        mock_pipeline_instance = MagicMock(spec=Pipeline)
        mock_pipeline_instance.model = mock_model
        mock_pipeline_instance.tokenizer = mock_tokenizer_instance
        mock_pipeline_instance.token = api_key
        mock_pipeline.return_value = mock_pipeline_instance

        # Initialize client
        client = HuggingFaceSeq2SeqSummarizationClient(mock_config, api_key)

        # Verify initialization
        mock_tokenizer.from_pretrained.assert_called_once()
        mock_automodel.from_pretrained.assert_called_once()
        mock_pipeline.assert_called_once()
        assert client.pipeline == mock_pipeline_instance
        assert client.api_key == api_key

    @patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.AutoTokenizer")
    @patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.AutoModelForSeq2SeqLM")
    @patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.pipeline")
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
        assert client.config.generation_config.max_new_tokens == 50

        # Now test with a value that's already within limits
        mock_config.generation_config.max_new_tokens = 30  # Less than max_position_embeddings
        # Initialize a new client
        client = HuggingFaceSeq2SeqSummarizationClient(mock_config)
        # Verify max_new_tokens was NOT adjusted since it was already within limits
        assert client.config.generation_config.max_new_tokens == 30


class TestHuggingFaceCausalLMClient:
    @pytest.fixture
    def mock_config(self):
        """Create a mock InferenceJobConfig for testing causal LM client."""
        config = MagicMock(spec=InferenceJobConfig)

        config.hf_pipeline = MagicMock()
        config.hf_pipeline.model_name_or_path = "mock-causal-model"
        config.hf_pipeline.task = TaskType.TEXT_GENERATION
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
        mock_pipeline_instance = MagicMock()
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


class TestHuggingFacePrefixTranslationClient:
    @pytest.fixture
    def mock_config(self):
        """Create a mock InferenceJobConfig for testing prefix translation client."""
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

        config.generation_config = MagicMock(spec=GenerationConfig)
        config.generation_config.max_new_tokens = 100
        return config

    @patch("model_clients.huggingface_clients.resolve_user_input_language")
    @patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.AutoTokenizer")
    @patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.AutoModelForSeq2SeqLM")
    @patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.pipeline")
    def test_initialization(self, mock_pipeline, mock_automodel, mock_tokenizer, mock_resolve_lang, mock_config):
        """Test initialization of the prefix translation client."""
        # Setup mocks
        mock_model = MagicMock()
        mock_model.config.max_position_embeddings = 512
        mock_automodel.from_pretrained.return_value = mock_model

        mock_tokenizer_instance = MagicMock(spec=PreTrainedTokenizer)
        mock_tokenizer_instance.model_max_length = 512
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance

        mock_pipeline_instance = MagicMock(spec=Pipeline)
        mock_pipeline_instance.model = mock_model
        mock_pipeline_instance.tokenizer = mock_tokenizer_instance
        mock_pipeline.return_value = mock_pipeline_instance

        # Mock language resolution
        mock_resolve_lang.side_effect = [
            {"iso_code": "en", "full_name": "English"},
            {"iso_code": "fr", "full_name": "French"},
        ]

        # Initialize client
        client = HuggingFacePrefixTranslationClient(mock_config)

        # Verify initialization
        mock_tokenizer.from_pretrained.assert_called_once()
        mock_automodel.from_pretrained.assert_called_once()
        mock_pipeline.assert_called_once()

        # Check that correct language parameters are set
        assert client.source_language_iso_code == "en"
        assert client.source_language == "English"
        assert client.target_language_iso_code == "fr"
        assert client.target_language == "French"
        assert client.prefix == "translate English to French: "

        # Verify pipeline was initialized with the correct task
        pipeline_args = mock_pipeline.call_args[1]
        assert pipeline_args["task"] == "translation_en_to_fr"
        assert client.pipeline == mock_pipeline_instance

    @patch("model_clients.huggingface_clients.resolve_user_input_language")
    @patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.AutoTokenizer")
    @patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.AutoModelForSeq2SeqLM")
    @patch("model_clients.mixins.huggingface_seq2seq_pipeline_mixin.pipeline")
    def test_predict(self, mock_pipeline, mock_automodel, mock_tokenizer, mock_resolve_lang, mock_config):
        """Test the predict method of the prefix translation client."""
        # Setup mocks
        mock_model = MagicMock()
        mock_model.config.max_position_embeddings = 512
        mock_automodel.from_pretrained.return_value = mock_model

        mock_tokenizer_instance = MagicMock(spec=PreTrainedTokenizer)
        mock_tokenizer_instance.model_max_length = 512
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance

        mock_pipeline_instance = MagicMock(spec=Pipeline)
        mock_pipeline_instance.model = mock_model
        mock_pipeline_instance.tokenizer = mock_tokenizer_instance
        mock_pipeline_instance.return_value = [
            {"translation_text": "Bonjour, comment ça va?"},
            {"translation_text": "Je suis un modèle de traduction."},
        ]
        mock_pipeline.return_value = mock_pipeline_instance

        # Set max_new_tokens in config
        mock_config.generation_config.max_new_tokens = 100

        # Mock language resolution
        mock_resolve_lang.side_effect = [
            {"iso_code": "en", "full_name": "English"},
            {"iso_code": "fr", "full_name": "French"},
        ]

        # Initialize client and call predict
        client = HuggingFacePrefixTranslationClient(mock_config)
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
