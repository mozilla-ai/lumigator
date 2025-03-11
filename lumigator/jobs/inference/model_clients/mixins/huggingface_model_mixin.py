from transformers import PreTrainedModel, TFPreTrainedModel

PreTrainedModelType = PreTrainedModel | TFPreTrainedModel


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
            return matched_params[0]
        else:
            raise ValueError(
                "No field corresponding to max_position_embeddings parameter found in model config"
                f" for {pretrained_model.config.name_or_path}."
                f" Checked alternative fields: {plausible_max_length_params}"
            )
