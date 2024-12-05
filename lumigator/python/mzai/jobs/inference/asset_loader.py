import torch
from accelerate import Accelerator
from inference_config import AutoModelConfig, AutoTokenizerConfig, QuantizationConfig
from loguru import logger
from paths import AssetPath, PathPrefix, strip_path_prefix
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    PretrainedConfig,
    PreTrainedModel,
    PreTrainedTokenizer,
)
from transformers.models.auto.modeling_auto import (
    MODEL_FOR_CAUSAL_LM_MAPPING_NAMES,
    MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING_NAMES,
)


def _resolve_asset_path(path: AssetPath) -> str:
    """Resolve an `AssetPath` to a loadable string path without the prefix."""
    raw_path = strip_path_prefix(path)
    if path.startswith(PathPrefix.HUGGINGFACE):
        return raw_path
    else:
        raise ValueError(f"Unable to resolve asset path from {path}.")


class HuggingFaceModelLoader:
    """Load Hugging Face models from a configuration."""

    def load_pretrained_config(
        self,
        config: AutoModelConfig,
    ) -> PretrainedConfig:
        """Load a `PretrainedConfig` from the model configuration.

        An exception is raised if the HuggingFace repo does not contain a `config.json` file.
        """
        config_path = _resolve_asset_path(config.path)
        return AutoConfig.from_pretrained(
            pretrained_model_name_or_path=config_path, trust_remote_code=config.trust_remote_code
        )

    def load_pretrained_model(
        self,
        config: AutoModelConfig,
        quantization: QuantizationConfig | None = None,
    ) -> PreTrainedModel:
        """Load a `PreTrainedModel` with optional quantization from the model configuration.

        An exception is raised if the HuggingFace repo does not contain a `config.json` file.

        TODO(RD2024-87): This fails if the checkpoint only contains a PEFT adapter config
        """
        device_map, bnb_config = None, None
        if quantization is not None:
            bnb_config = quantization.as_huggingface()
            # When quantization is enabled, model must all be on same GPU to work with DDP
            # If a device_map is not specified we will get accelerate errors downstream
            # Reference: https://github.com/huggingface/accelerate/issues/1840#issuecomment-1683105994
            current_device = (
                Accelerator().local_process_index if torch.cuda.is_available() else "cpu"
            )
            device_map = {"": current_device}
            logger.info(f"Setting model device_map = {device_map} to enable quantization")

        # TODO: HuggingFace has many AutoModel classes with different "language model heads."
        # Can we abstract this to load with any type of AutoModel class?
        model_path = _resolve_asset_path(config.path)

        # load config first to get the model type
        model_config = self.load_pretrained_config(config)

        if model_config.model_type in MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING_NAMES:
            automodel_class = AutoModelForSeq2SeqLM
        elif model_config.model_type in MODEL_FOR_CAUSAL_LM_MAPPING_NAMES:
            automodel_class = AutoModelForCausalLM
        else:
            logger.info("Model type not supported. Trying AutoModelForCausalLM")
            automodel_class = AutoModelForCausalLM

        return automodel_class.from_pretrained(
            pretrained_model_name_or_path=model_path,
            trust_remote_code=config.trust_remote_code,
            torch_dtype=config.torch_dtype,
            quantization_config=bnb_config,
            device_map=device_map,
        )


class HuggingFaceTokenizerLoader:
    """Helper class for loading HuggingFace tokenizers from LM Buddy configurations."""

    def load_pretrained_tokenizer(self, config: AutoTokenizerConfig) -> PreTrainedTokenizer:
        """Load a `PreTrainedTokenizer` from the model configuration.

        An exception is raised if the HuggingFace repo does not contain a `tokenizer.json` file.
        """
        tokenizer_path = _resolve_asset_path(config.path)
        tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=tokenizer_path,
            trust_remote_code=config.trust_remote_code,
            use_fast=config.use_fast,
            model_max_length=config.mod_max_length,
        )
        if tokenizer.pad_token_id is None:
            # Pad token required for generating consistent batch sizes
            tokenizer.pad_token_id = tokenizer.eos_token_id
        return tokenizer
