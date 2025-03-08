from inference_config import GenerationConfig
from loguru import logger


class GenerationConfigMixin:
    """Mixin to handle ``max_new_tokens`` configuration in the generation config"""

    def adjust_config_max_new_tokens(self, config: GenerationConfig, max_pos_emb: int | None) -> GenerationConfig:
        """Adjust the max_new_tokens value in the generation config.

        This method mutates the ``max_new_tokens`` attribute of the ``GenerationConfig`` parameter.

        :param config: The generation configuration.
        :param max_pos_emb: The maximum position embeddings supported by the model.
        :returns: The updated generation configuration.
        :raises TypeError: If the config is None.
        """
        if config is None:
            raise TypeError("The config cannot be None")

        # Setting output sequence generation max tokens
        # If the user has set a max_new_tokens to be generated
        # we need to make sure it's not bigger than the model's max_position_embeddings.
        if not config.max_new_tokens:
            logger.info(f"Setting max_length to the max supported length by the model: {max_pos_emb}")
            config.max_new_tokens = max_pos_emb
            return config

        if config.max_new_tokens > max_pos_emb:
            logger.warning(
                f"Requested {config.max_new_tokens} tokens, but model supports only {max_pos_emb}. "
                f"Setting max_length to {max_pos_emb}"
            )
            config.max_new_tokens = max_pos_emb
        else:
            logger.info(f"Setting max_length to {config.max_new_tokens}")

        return config
