from inference_config import HfPipelineConfig, TaskType
from loguru import logger
from transformers import (
    AutoModel,
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    Pipeline,
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
    TFPreTrainedModel,
    pipeline,
)

TransformersTokenizerType = PreTrainedTokenizer | PreTrainedTokenizerFast
TransformersModelType = PreTrainedModel | TFPreTrainedModel


class HuggingFacePipelineMixin:
    """Mixin to handle pipeline related initialization and adjustment."""

    def initialize_model(self, pipeline_config: HfPipelineConfig) -> AutoModel | AutoModelForSeq2SeqLM:
        """Initialize the model using the provided configuration based on task type.

        :param pipeline_config: The HuggingFace pipeline configuration.
        :returns: The initialized model.
        :raises TypeError: If the pipeline_config is None.
        """
        if pipeline_config is None:
            raise TypeError("The pipeline_config cannot be None")

        # Use AutoModelForSeq2SeqLM for tasks like summarization, text generation or translation
        if pipeline_config.task in [TaskType.SUMMARIZATION, TaskType.TEXT_GENERATION, TaskType.TRANSLATION]:
            return AutoModelForSeq2SeqLM.from_pretrained(
                pipeline_config.model_name_or_path,
                trust_remote_code=pipeline_config.trust_remote_code,
                torch_dtype=pipeline_config.torch_dtype,
            )
        else:
            return AutoModel.from_pretrained(
                pipeline_config.model_name_or_path,
                trust_remote_code=pipeline_config.trust_remote_code,
                torch_dtype=pipeline_config.torch_dtype,
            )

    def initialize_tokenizer(self, pipeline_config: HfPipelineConfig) -> AutoTokenizer:
        """Initialize the tokenizer using the provided configuration.

        :param pipeline_config: The HuggingFace pipeline configuration.
        :returns: The initialized tokenizer.
        :raises TypeError: If the pipeline_config is None.
        """
        if pipeline_config is None:
            raise TypeError("The pipeline_config cannot be None")

        return AutoTokenizer.from_pretrained(
            pipeline_config.model_name_or_path,
            use_fast=pipeline_config.use_fast,
            trust_remote_code=pipeline_config.trust_remote_code,
        )

    def initialize_pipeline(
        self, pipeline_config: HfPipelineConfig, model: TransformersModelType, tokenizer: TransformersTokenizerType
    ) -> Pipeline:
        """Initialize the pipeline using the provided model and tokenizer.

        :param model: The model to be used in the pipeline.
        :param tokenizer: The tokenizer to be used in the pipeline.
        :param pipeline_config: The HuggingFace pipeline configuration.
        :returns: The initialized pipeline object.
        :raises TypeError: If any of the parameters are None.
        """
        if model is None:
            raise TypeError("The model cannot be None")
        if tokenizer is None:
            raise TypeError("The tokenizer cannot be None")
        if pipeline_config is None:
            raise TypeError("The pipeline_config cannot be None")

        # Drop any parameters we are sending explicitly, but ensure anything is allowed to be passed to the pipeline.
        pipeline_kwargs = pipeline_config.model_dump(
            exclude_unset=True, exclude={"model_config", "task", "revision", "device", "model", "tokenizer"}
        )

        pipeline_obj = pipeline(
            task=pipeline_config.task,
            revision=pipeline_config.revision,
            device=pipeline_config.device,
            model=model,
            tokenizer=tokenizer,
            **pipeline_kwargs,
        )

        return pipeline_obj

    def adjust_tokenizer_max_length(self, pipeline: Pipeline, max_pos_emb: int | None) -> None:
        """When max position embeddings (``max_pos_emb``) is positive and less than the pipeline's tokenizer max length,
        adjusts the tokenizer max length to match the supplied parameter.

        This method mutates the ``model_max_length`` attribute of the ``tokenizer`` in the ``pipeline`` parameter.

        :param pipeline: The HuggingFace pipeline object.
        :param max_pos_emb: The maximum position embeddings supported by the model.
        :returns: None
        :raises TypeError: If the pipeline or its tokenizer is None.
        """
        if pipeline is None:
            raise TypeError("The pipeline cannot be None")
        if pipeline.tokenizer is None:
            raise TypeError("The pipeline's tokenizer cannot be None")

        if max_pos_emb is None or pipeline.tokenizer.model_max_length <= max_pos_emb:
            return

        logger.warning(
            f"Tokenizer model_max_length ({pipeline.tokenizer.model_max_length}) "
            f"is bigger than the model's max_position_embeddings ({max_pos_emb})."
        )
        pipeline.tokenizer.model_max_length = max_pos_emb
