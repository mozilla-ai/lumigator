from loguru import logger
from transformers import PreTrainedModel, TFPreTrainedModel

PreTrainedModelType = PreTrainedModel | TFPreTrainedModel

DEFAULT_MAX_POSITION_EMBEDDINGS = 512


class HuggingFaceModelMixin:
    """Mixin to handle model initialization and configuration."""

    def get_max_position_embeddings(self, pretrained_model: PreTrainedModelType) -> int:
        """Extract the maximum position embeddings from the model configuration.

        :param pretrained_model: The pre-trained model from which to extract the max position embeddings.
        :returns: The maximum position embeddings value.
        :raises ValueError: If no valid ``max_position_embeddings`` found in the model config.
        :raises TypeError: If the pre-trained model or its config is None.
        """
        if pretrained_model is None:
            raise TypeError("The pre-trained model cannot be None")
        if pretrained_model.config is None:
            raise TypeError("The pre-trained model's config cannot be None")

        # Setting input sequence max tokens:
        # Taken from https://stackoverflow.com/a/78737021
        # Different LLM model families use different names for the same field.
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
            getattr(pretrained_model.config, param)
            for param in plausible_max_length_params
            if param in dir(pretrained_model.config)
        ]
        # Grab the first one in the list; usually there's only 1 anyway
        if len(matched_params):
            max_pos_emb = matched_params[0]
        else:
            # If none of the plausible fields are found (e.g. google/mt5 model family), use a default value
            max_pos_emb = DEFAULT_MAX_POSITION_EMBEDDINGS
            logger.warning(
                "No field corresponding to max_position_embeddings parameter found"
                f" for {self.config.hf_pipeline.model_name_or_path}."
                f" Checked alternative fields: {plausible_max_length_params}"
                f" Setting max_position_embeddings to default value: {DEFAULT_MAX_POSITION_EMBEDDINGS}"
            )

        return max_pos_emb
