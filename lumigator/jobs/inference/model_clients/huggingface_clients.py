from inference_config import InferenceJobConfig
from loguru import logger
from lumigator_schemas.tasks import TaskType
from model_clients.base_client import BaseModelClient
from model_clients.translation_utils import load_translation_config, resolve_user_input_language
from transformers import AutoConfig, AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

from schemas import PredictionResult

DEFAULT_MAX_POSITION_EMBEDDINGS = 512


class HuggingFaceModelClientFactory:
    """Factory class that creates the appropriate specialized client"""

    @staticmethod
    def create(config: InferenceJobConfig) -> BaseModelClient:
        """Factory method to create the appropriate client based on config"""
        model_name = config.hf_pipeline.model_name_or_path
        task = config.hf_pipeline.task_definition.task

        # Load model config to determine architecture - Seq2Seq or CausalLM
        model_config = AutoConfig.from_pretrained(model_name, trust_remote_code=config.hf_pipeline.trust_remote_code)

        # Summarization task with Seq2Seq model
        if task == TaskType.SUMMARIZATION and model_config.is_encoder_decoder:
            logger.info(f"Running inference with HuggingFaceSeq2SeqSummarizationClient for {model_name}")
            return HuggingFaceSeq2SeqSummarizationClient(config)

        elif task == TaskType.TRANSLATION and model_config.is_encoder_decoder:
            # Load the translation models configuration
            translation_config = load_translation_config()

            prefix_models = translation_config.get("prefix_translation_models", [])
            if model_name in prefix_models:
                logger.info(f"Running inference with HuggingFacePrefixTranslationClient for {model_name}")
                return HuggingFacePrefixTranslationClient(config)
            else:
                logger.error(
                    f"Translation task with HF seq2seq models: {model_name} is not supported. "
                    f"Check translation_models.yaml for supported models."
                )

        # Default to CausalLM for the general text-generation task
        else:
            logger.info(f"Running inference with HuggingFaceCausalLMClient for {model_name}")
            return HuggingFaceCausalLMClient(config)


class HuggingFaceSeq2SeqModelClientMixin:
    """Mixin with common functionality for seq2seq models"""

    def _initialize_model_and_tokenizer(self, config, pipeline_task=None):
        """Initialize the model and tokenizer for the seq2seq models"""
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.hf_pipeline.model_name_or_path,
            use_fast=config.hf_pipeline.use_fast,
            trust_remote_code=config.hf_pipeline.trust_remote_code,
        )

        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            config.hf_pipeline.model_name_or_path,
            trust_remote_code=config.hf_pipeline.trust_remote_code,
            torch_dtype=config.hf_pipeline.torch_dtype,
        )

        self._pipeline = pipeline(
            task=config.hf_pipeline.task_definition.task if not pipeline_task else pipeline_task,
            model=self.model,
            tokenizer=self.tokenizer,
            revision=config.hf_pipeline.revision,
            device=config.hf_pipeline.device,
        )
        self._set_seq2seq_max_length()

    def _set_seq2seq_max_length(self):
        """Make sure that the model can actually support the max_new_tokens configured.
        For the Seq2Seq models, the max_length is the max_position_embeddings. That's because the input and output
        tokens have separate positions, so the model can generate upto max_position_embeddings tokens.
        This isn't true if it's a CausalLM model, since the output token positions would be len(input) + len(output).
        """
        # 1. Setting input sequence max tokens
        # Taken from https://stackoverflow.com/a/78737021
        # Different LLM model families use different names for the same field
        plausible_max_length_params = [
            "max_position_embeddings",
            "n_positions",
            "n_ctx",
            "seq_len",
            "seq_length",
            "max_sequence_length",
            "sliding_window",
        ]
        # Check which attribute a given model config object has
        matched_params = [
            getattr(self._pipeline.model.config, param)
            for param in plausible_max_length_params
            if param in dir(self._pipeline.model.config)
        ]
        # Grab the first one in the list; usually there's only 1 anyway
        if len(matched_params):
            max_pos_emb = matched_params[0]
        else:
            # If none of the plausible fields are found (e.g. google/mt5 model family), use a default value
            max_pos_emb = DEFAULT_MAX_POSITION_EMBEDDINGS
            logger.warning(
                "No field corresponding to max_position_embeddings parameter found"
                f" for {self._config.hf_pipeline.model_name_or_path}."
                f" Checked alternative fields: {plausible_max_length_params}"
            )

        # If the model is of the HF Hub the odds of this being wrong are low, but it's still good to check that the
        # tokenizer model and the model have the same max_position_embeddings
        if self._pipeline.tokenizer.model_max_length > max_pos_emb:
            logger.warning(
                f"Tokenizer model_max_length ({self._pipeline.tokenizer.model_max_length})"
                f" is bigger than the model's max_position_embeddings ({max_pos_emb})"
                " Setting the tokenizer model_max_length to the model's max_position_embeddings."
            )
            self._pipeline.tokenizer.model_max_length = max_pos_emb

        # 2. Setting output sequence generation max tokens
        # If the user has set a max_new_tokens to be generated
        # we need to make sure it's not bigger than the model's max_position_embeddings
        if self._config.generation_config.max_new_tokens:
            if self._config.generation_config.max_new_tokens > max_pos_emb:
                logger.warning(
                    f"Model can generate {max_pos_emb} tokens."
                    f" Requested {self._config.generation_config.max_new_tokens}."
                    f" Setting max_length to {max_pos_emb}."
                )
                self._config.generation_config.max_new_tokens = max_pos_emb
            else:
                logger.info(f"Setting max_length to {self._config.generation_config.max_new_tokens}")
        else:
            logger.info(
                f"Setting max_length to the max supported length by the model by its position embeddings: {max_pos_emb}"
            )
            self._config.generation_config.max_new_tokens = max_pos_emb


class HuggingFaceSeq2SeqSummarizationClient(BaseModelClient, HuggingFaceSeq2SeqModelClientMixin):
    """Client for seq2seq summarization models
    When using HF pipeline with 'summarization' task, it has to go through Seq2Seq models
    https://huggingface.co/docs/transformers/en/main_classes/pipelines#transformers.SummarizationPipeline
    """

    def __init__(self, config: InferenceJobConfig):
        self._config = config
        self._initialize_model_and_tokenizer(config)

    def predict(self, prompt) -> PredictionResult:
        generation = self._pipeline(
            prompt, max_new_tokens=self._config.generation_config.max_new_tokens, truncation=True
        )[0]

        return PredictionResult(
            prediction=generation["summary_text"],
        )


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

    def __init__(self, config: InferenceJobConfig):
        self._config = config
        self._system_prompt = config.system_prompt

        # CausalLM models supported for summarization and translation tasks through system_prompt
        # HF pipeline task overwritten to 'text-generation' since these causalLMs are not task-specific models
        pipeline_config = config.hf_pipeline.model_dump()
        pipeline_config["task"] = TaskType.TEXT_GENERATION

        self._pipeline = pipeline(**pipeline_config)

    def predict(self, prompt) -> PredictionResult:
        messages = [
            {"role": "system", "content": self._system_prompt},
            {"role": "user", "content": prompt},
        ]

        generation = self._pipeline(messages, max_new_tokens=self._config.generation_config.max_new_tokens)[0]

        return PredictionResult(
            prediction=generation["generated_text"][-1]["content"],
        )


class HuggingFacePrefixTranslationClient(BaseModelClient, HuggingFaceSeq2SeqModelClientMixin):
    """Client for T5-style models that use prefixes for translation"""

    def __init__(self, config: InferenceJobConfig):
        self._config = config
        source_language_user_input = getattr(config.hf_pipeline.task_definition, "source_language", None)
        target_language_user_input = getattr(config.hf_pipeline.task_definition, "target_language", None)

        if not source_language_user_input or not target_language_user_input:
            raise ValueError("Source and target languages must be provided for translation task.")

        source_language_info = resolve_user_input_language(source_language_user_input)
        target_language_info = resolve_user_input_language(target_language_user_input)

        self._source_language_iso_code = source_language_info["iso_code"]  # e.g. "en"
        self._source_language = source_language_info["full_name"]  # e.g. "English"
        self._target_language_iso_code = target_language_info["iso_code"]  # e.g. "de"
        self._target_language = target_language_info["full_name"]  # e.g. "German"

        # Set the task to translation with the source and target languages
        pipeline_task = (
            f"{TaskType.TRANSLATION.value}_{self._source_language_iso_code}_to_{self._target_language_iso_code}"
        )
        self._initialize_model_and_tokenizer(self._config, pipeline_task)

    def predict(self, prompt) -> PredictionResult:
        prefix = f"translate {self._source_language} to {self._target_language}: "
        prefixed_prompt = prefix + prompt

        result = self._pipeline(prefixed_prompt, max_new_tokens=self._config.generation_config.max_new_tokens)[0]

        return PredictionResult(
            prediction=result["translation_text"],
        )
