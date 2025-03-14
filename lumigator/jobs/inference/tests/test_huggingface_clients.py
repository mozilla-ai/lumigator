from unittest.mock import MagicMock, patch

import pytest
from inference_config import GenerationConfig, HfPipelineConfig, InferenceJobConfig
from lumigator_schemas.tasks import TaskDefinition, TaskType
from model_clients.huggingface_clients import (
    HuggingFaceCausalLMClient,
    HuggingFaceLanguageCodeTranslationClient,
    HuggingFacePrefixTranslationClient,
    HuggingFaceSeq2SeqSummarizationClient,
)
from transformers import Pipeline, PreTrainedTokenizer

from schemas import PredictionResult

TEST_PROMPT = [
    [{"role": "system", "content": "You are a helpfull assistant."}, {"role": "user", "content": "Test prompt"}]
]


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
                {"iso_code": "en", "full_name": "English"},
                {"iso_code": "fr", "full_name": "French"},
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
