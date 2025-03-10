from inference_config import InferenceJobConfig
from loguru import logger
from model_clients.base_client import BaseModelClient
from model_clients.mixins.generation_config_mixin import GenerationConfigMixin
from model_clients.mixins.huggingface_model_mixin import HuggingFaceModelMixin
from model_clients.mixins.huggingface_pipeline_mixin import HuggingFacePipelineMixin
from transformers import AutoConfig, pipeline

from schemas import PredictionResult, TaskType


class HuggingFaceModelClientFactory:
    """Factory class that creates the appropriate specialized client"""

    @staticmethod
    def create(config: InferenceJobConfig) -> BaseModelClient:
        """Factory method to create the appropriate client based on config"""
        model_name = config.hf_pipeline.model_name_or_path
        task = config.hf_pipeline.task

        # Load model config to determine architecture - Seq2Seq or CausalLM
        model_config = AutoConfig.from_pretrained(model_name, trust_remote_code=config.hf_pipeline.trust_remote_code)

        # Summarization task with Seq2Seq model
        if task == TaskType.SUMMARIZATION and model_config.is_encoder_decoder:
            logger.info(f"Running inference with HuggingFaceSeq2SeqSummarizationClient for {model_name}")
            return HuggingFaceSeq2SeqSummarizationClient(config)

        # Default to CausalLM for the general text-generation task
        else:
            logger.info(f"Running inference with HuggingFaceCausalLMClient for {model_name}")
            return HuggingFaceCausalLMClient(config)


class HuggingFaceSeq2SeqSummarizationClient(
    BaseModelClient,
    HuggingFaceModelMixin,
    HuggingFacePipelineMixin,
    GenerationConfigMixin,
):
    """Client for seq2seq summarization models.

    When using HF pipeline with 'summarization' task, it has to go through Seq2Seq models
    https://huggingface.co/docs/transformers/en/main_classes/pipelines#transformers.SummarizationPipeline
    """

    def __init__(self, config: InferenceJobConfig):
        self.config = config
        self.model = self.initialize_model(self.config.hf_pipeline)
        self.tokenizer = self.initialize_tokenizer(self.config.hf_pipeline)
        self.pipeline = self.initialize_pipeline(self.config.hf_pipeline, self.model, self.tokenizer)
        self.set_seq2seq_max_length()

    def set_seq2seq_max_length(self):
        """Set the maximum sequence length for the seq2seq model.

        This method ensures that the tokenizer and model have the same maximum position embeddings
        and adjusts the generation configuration accordingly.
        """
        # If the model is of the HF Hub the odds of this being wrong are low, but it's still good to check that the
        # tokenizer model and the model have the same max_position_embeddings.
        max_pos_emb = self.get_max_position_embeddings(self.pipeline.model)
        self.adjust_tokenizer_max_length(self.pipeline, max_pos_emb)
        # Adjust output sequence generation max tokens.
        self.adjust_config_max_new_tokens(self.config.generation_config, max_pos_emb)

    def predict(self, prompt) -> PredictionResult:
        generation = self.pipeline(
            prompt, max_new_tokens=self.config.generation_config.max_new_tokens, truncation=True
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
        self.config = config
        self.system_prompt = config.system_prompt

        # CausalLM models supported for summarization and translation tasks through system_prompt
        # HF pipeline task overwritten to 'text-generation' since these causalLMs are not task-specific models
        pipeline_config = config.hf_pipeline.model_dump()
        pipeline_config["task"] = TaskType.TEXT_GENERATION

        self.pipeline = pipeline(**pipeline_config)

    def predict(self, prompt) -> PredictionResult:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        generation = self.pipeline(messages, max_new_tokens=self.config.generation_config.max_new_tokens)[0]

        return PredictionResult(
            prediction=generation["generated_text"][-1]["content"],
        )
