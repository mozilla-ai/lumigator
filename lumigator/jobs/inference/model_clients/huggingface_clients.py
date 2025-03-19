from inference_config import InferenceJobConfig
from loguru import logger
from lumigator_schemas.tasks import TaskType
from model_clients.base_client import BaseModelClient
from model_clients.mixins.generation_config_mixin import GenerationConfigMixin
from model_clients.mixins.huggingface_model_mixin import HuggingFaceModelMixin
from model_clients.mixins.huggingface_seq2seq_pipeline_mixin import HuggingFaceSeq2SeqPipelineMixin
from model_clients.mixins.language_code_mixin import LanguageCodesSetupMixin
from model_clients.translation_utils import load_translation_config
from transformers import AutoConfig, pipeline

from schemas import PredictionResult


def is_encoder_decoder(model_name: str) -> bool:
    """Check if the model is an encoder-decoder model."""
    return model_name.startswith("Helsinki-NLP/opus-mt") or AutoConfig.from_pretrained(model_name).is_encoder_decoder


class HuggingFaceModelClientFactory:
    """Factory class that creates the appropriate specialized client"""

    @staticmethod
    def create(config: InferenceJobConfig, api_key: str | None = None) -> BaseModelClient:
        """Factory method to create the appropriate client based on config"""
        model_name = config.hf_pipeline.model_name_or_path
        is_model_encoder_decoder = is_encoder_decoder(model_name)
        task = config.task_definition.task

        # Summarization task with Seq2Seq model
        if task == TaskType.SUMMARIZATION and is_model_encoder_decoder:
            logger.info(f"Running inference with HuggingFaceSeq2SeqSummarizationClient for {model_name}")
            return HuggingFaceSeq2SeqSummarizationClient(config, api_key)

        elif task == TaskType.TRANSLATION and is_model_encoder_decoder:
            # Load the supported translation model families configuration
            translation_config = load_translation_config()

            if model_name in translation_config["prefix_based"]:
                logger.info(f"Running inference with HuggingFacePrefixTranslationClient for {model_name}")
                return HuggingFacePrefixTranslationClient(config, api_key)
            elif model_name in translation_config["language_code_based"]:
                logger.info(f"Running inference with HuggingFaceLanguageCodeTranslationClient for {model_name}")
                return HuggingFaceLanguageCodeTranslationClient(config, api_key)
            elif HuggingFaceOpusMTTranslationClient.is_model_type_marianmt(model_name):
                logger.info(f"Running inference with HuggingFaceOpusMTTranslationClient for {model_name}")
                return HuggingFaceOpusMTTranslationClient(config, api_key)
            else:
                logger.error(
                    f"Translation task with HF seq2seq models: {model_name} is not supported. "
                    f"Only models in translation_models.yaml and OpusMT models are currently supported."
                )

        # Default to CausalLM for the general text-generation task
        else:
            logger.info(f"Running inference with HuggingFaceCausalLMClient for {model_name}")
            return HuggingFaceCausalLMClient(config, api_key)


class HuggingFaceSeq2SeqSummarizationClient(
    BaseModelClient,
    HuggingFaceModelMixin,
    HuggingFaceSeq2SeqPipelineMixin,
    GenerationConfigMixin,
):
    """Client for seq2seq summarization models.

    When using HF pipeline with 'summarization' task, it has to go through Seq2Seq models
    https://huggingface.co/docs/transformers/en/main_classes/pipelines#transformers.SummarizationPipeline
    """

    def __init__(self, config: InferenceJobConfig, api_key: str | None = None):
        self.config = config
        self.api_key = api_key
        self.model = self.initialize_model(self.config.hf_pipeline)
        self.tokenizer = self.initialize_tokenizer(self.config.hf_pipeline)
        self.pipeline = self.initialize_pipeline(self.config.hf_pipeline, self.model, self.tokenizer, api_key=api_key)
        self.set_seq2seq_max_length()

    def predict(self, examples: list) -> list[PredictionResult]:
        generations = self.pipeline(
            examples, max_new_tokens=self.config.generation_config.max_new_tokens, truncation=True
        )

        prediction_results = []
        for generation in generations:
            prediction_result = PredictionResult(prediction=generation["summary_text"])
            prediction_results.append(prediction_result)

        return prediction_results


class HuggingFaceCausalLMClient(BaseModelClient):
    """Client for causal language models
    CausalLM models can be used for text-generation or summarization
    or translation tasks with right system_prompt.

    When using a text-generation model, the pipeline returns a dictionary with a single key,
    'generated_text'. The value of this key is a list of dictionaries, each containing the\
    role and content of a message. For example:
    [{'role': 'system', 'content': 'You are a helpful assistant.'},
     {'role': 'user', 'content': 'What is the capital of France?'}, ...]

    We want to return the content of the last message in the list, which is the model's
    response to the prompt.
    """

    def __init__(self, config: InferenceJobConfig, api_key: str | None = None):
        self.config = config
        self.api_key = api_key

        # CausalLM models supported for summarization and translation tasks through system_prompt
        # HF pipeline task overwritten to 'text-generation' since these causalLMs are not task-specific models
        pipeline_config = config.hf_pipeline.model_dump()
        pipeline_config["task"] = TaskType.TEXT_GENERATION
        pipeline_config["token"] = self.api_key

        self.pipeline = pipeline(**pipeline_config)

    def predict(self, examples: list[list[dict[str, str]]]) -> list[PredictionResult]:
        generations = self.pipeline(examples, max_new_tokens=self.config.generation_config.max_new_tokens)

        prediction_results = []
        for generation in generations:
            prediction_result = PredictionResult(prediction=generation[0]["generated_text"][-1]["content"])
            prediction_results.append(prediction_result)

        return prediction_results


class HuggingFacePrefixTranslationClient(
    BaseModelClient,
    HuggingFaceModelMixin,
    HuggingFaceSeq2SeqPipelineMixin,
    GenerationConfigMixin,
    LanguageCodesSetupMixin,
):
    """Client for T5-style models that use prefixes for translation"""

    def __init__(self, config: InferenceJobConfig, api_key: str | None = None):
        self.config = config
        self.api_key = api_key
        self.setup_translation_languages(config.task_definition)
        self.model = self.initialize_model(self.config.hf_pipeline)
        self.tokenizer = self.initialize_tokenizer(self.config.hf_pipeline)

        # Modify the task to include the the source and target languages
        specific_pipeline_task = (
            f"{TaskType.TRANSLATION.value}_{self.source_language_iso_code}_to_{self.target_language_iso_code}"
        )
        self.pipeline = self.initialize_pipeline(
            self.config.hf_pipeline,
            self.model,
            self.tokenizer,
            specific_pipeline_task=specific_pipeline_task,
            api_key=api_key,
        )
        self.set_seq2seq_max_length()
        self.prefix = f"translate {self.source_language} to {self.target_language}: "

    def predict(self, examples: list) -> list[PredictionResult]:
        prefixed_examples = [self.prefix + example for example in examples]

        generations = self.pipeline(
            prefixed_examples, max_new_tokens=self.config.generation_config.max_new_tokens, truncation=True
        )

        prediction_results = []
        for generation in generations:
            prediction_result = PredictionResult(prediction=generation["translation_text"])
            prediction_results.append(prediction_result)

        return prediction_results


class HuggingFaceLanguageCodeTranslationClient(
    BaseModelClient,
    HuggingFaceModelMixin,
    HuggingFaceSeq2SeqPipelineMixin,
    GenerationConfigMixin,
    LanguageCodesSetupMixin,
):
    """Client for translation models that require language codes (mBART, NLLB, M2M)"""

    def __init__(self, config: InferenceJobConfig, api_key: str | None = None):
        self.config = config
        self.api_key = api_key
        self.setup_translation_languages(config.task_definition)
        self.model = self.initialize_model(self.config.hf_pipeline)
        self.tokenizer = self.initialize_tokenizer(self.config.hf_pipeline)

        self.pipeline = self.initialize_pipeline(self.config.hf_pipeline, self.model, self.tokenizer, api_key=api_key)
        self.set_seq2seq_max_length()

    def predict(self, examples: str | list[list[dict[str, str]]]) -> list[PredictionResult]:
        generations = self.pipeline(
            examples,
            max_new_tokens=self.config.generation_config.max_new_tokens,
            truncation=True,
            src_lang=self.source_language_iso_code,
            tgt_lang=self.target_language_iso_code,
        )

        prediction_results = []
        for generation in generations:
            prediction_result = PredictionResult(prediction=generation["translation_text"])
            prediction_results.append(prediction_result)

        return prediction_results


class HuggingFaceOpusMTTranslationClient(
    BaseModelClient,
    HuggingFaceModelMixin,
    HuggingFaceSeq2SeqPipelineMixin,
    GenerationConfigMixin,
    LanguageCodesSetupMixin,
):
    """Client for OpusMT/MarianMT models"""

    def __init__(self, config: InferenceJobConfig, api_key: str | None = None):
        self.config = config
        self.api_key = api_key
        self.setup_translation_languages(config.task_definition)
        self.configure_model_name()
        self.model = self.initialize_model(self.config.hf_pipeline)
        self.tokenizer = self.initialize_tokenizer(self.config.hf_pipeline)
        self.pipeline = self.initialize_pipeline(self.config.hf_pipeline, self.model, self.tokenizer, api_key=api_key)
        self.set_seq2seq_max_length()
        # Set up prefix string for target language. Required for multilingual versions:
        # https://huggingface.co/Helsinki-NLP/opus-mt-tc-bible-big-mul-deu_eng_fra_por_spa#how-to-get-started-with-the-model
        self.target_language_prefix_string = f">>{self.target_language_alpha3_code}<< "

    @staticmethod
    def is_model_type_marianmt(model_name_or_path: str) -> bool:
        """Check if the model is a MarianMT model."""
        if model_name_or_path.startswith("Helsinki-NLP/opus-mt"):
            return True
        config = AutoConfig.from_pretrained(model_name_or_path)
        return config.model_type == "marian"

    def configure_model_name(self):
        """Configure the model name based on the source and target language codes
        if generic name Helsinki-NLP/opus-mt is used.
        """
        if self.config.hf_pipeline.model_name_or_path == "Helsinki-NLP/opus-mt":
            # User has not specified an exact model name, so we will use the default model for the language pair
            self.config.hf_pipeline.model_name_or_path = (
                f"Helsinki-NLP/opus-mt-{self.source_language_iso_code}-{self.target_language_iso_code}"
            )
            try:
                AutoConfig.from_pretrained(self.config.hf_pipeline.model_name_or_path)
                logger.info(
                    f"Using default Opus MT model for language pair: {self.config.hf_pipeline.model_name_or_path}"
                )
            except Exception as e:
                raise ValueError(
                    f"Model {self.config.hf_pipeline.model_name_or_path} not found on Hugging Face Hub. "
                    "Please specify the exact Opus MT that you would like to use."
                ) from e
        else:
            # User has specified an exact model name, so we use that
            logger.info(
                f"Using model: {self.config.hf_pipeline.model_name_or_path} which is different "
                "from the default Opus MT model for the language pair: "
                f"Helsinki-NLP/opus-mt-{self.source_language_iso_code}-{self.target_language_iso_code}"
            )

    def predict(self, examples: list) -> list[PredictionResult]:
        prefixed_examples = [self.target_language_prefix_string + example for example in examples]
        logger.info(f"Prefixed examples: {prefixed_examples}")

        generations = self.pipeline(
            prefixed_examples, max_new_tokens=self.config.generation_config.max_new_tokens, truncation=True
        )

        prediction_results = []
        for generation in generations:
            prediction_result = PredictionResult(prediction=generation["translation_text"])
            prediction_results.append(prediction_result)

        return prediction_results
