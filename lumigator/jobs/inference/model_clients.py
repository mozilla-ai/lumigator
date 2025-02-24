import re
from abc import abstractmethod

from inference_config import InferenceJobConfig
from litellm import completion
from loguru import logger
from transformers import pipeline
from transformers.tokenization_utils_base import VERY_LARGE_INTEGER


def strip_path_prefix(path: str) -> str:
    """Strip the 'scheme://' prefix from the start of a string."""
    pattern = "^\w+\:\/\/"
    return re.sub(pattern, "", path)


class BaseModelClient:
    """Abstract class for a model client, used to provide a uniform interface
    (currentnly just a simple predict method) to models served in different
    ways (e.g. HF models loaded locally, OpenAI endpoints, vLLM inference
    servers, llamafile).
    """

    @abstractmethod
    def __init__(self, model: str, config: InferenceJobConfig):
        """Used to initialize the model / inference service."""
        pass

    @abstractmethod
    def predict(self, prompt: str) -> str:
        """Given a prompt, return a prediction."""
        pass


class LiteLLMModelClient(BaseModelClient):
    """Model client for models served via openai-compatible API.
    For OpenAI models:
    - The base_url is fixed
    - Choose an model name (see https://platform.openai.com/docs/models)
    - Customize the system prompt if needed

    For compatible models:
    - Works with local/remote vLLM-served models and llamafiles
    - Provide base_url and model
    - Customize the system prompt if needed
    """

    def __init__(self, config: InferenceJobConfig):
        self.config = config
        self.system = "You are a helpful assisant., please summarize the given input."
        logger.info(f"LiteLLMModelClient initialized with config: {config}")

    def predict(
        self,
        prompt: str,
    ) -> str:
        litellm_model = f"{self.config.inference_server.provider}/{self.config.inference_server.model}"
        logger.info(f"Sending request to {litellm_model}")
        response = completion(
            model=litellm_model,
            messages=[
                {"role": "system", "content": self.system},
                {"role": "user", "content": prompt},
            ],
            max_tokens=self.config.params.max_tokens,
            frequency_penalty=self.config.params.frequency_penalty,
            temperature=self.config.params.temperature,
            top_p=self.config.params.top_p,
            drop_params=True,
            api_base=self.config.inference_server.base_url if self.config.inference_server else None,
        )
        # LiteLLM gives us the cost of each API which is nice.
        # Eventually we can add this to the response object as well.
        cost = response._hidden_params["response_cost"]
        logger.info(f"Response cost: {cost}")
        return response.choices[0].message.content


class HuggingFaceModelClient(BaseModelClient):
    def __init__(self, config: InferenceJobConfig):
        logger.info(f"System prompt: {config.system_prompt}")
        self._system = config.system_prompt
        self._task = config.hf_pipeline.task
        self._pipeline = pipeline(**config.hf_pipeline.model_dump())
        self._set_tokenizer_max_length()

    def _set_tokenizer_max_length(self):
        """Set the tokenizer's model_max_length if it's currently the default very large integer.
        Checks various possible max_length parameters which varies on model architecture.
        """
        config = self._pipeline.model.config
        logger.info(
            f"Selected HF model's tokenizer has maximum number of input tokens: \
                    {self._pipeline.tokenizer.model_max_length}"
        )
        # If suitable model_max_length is already available, don't override it
        if self._pipeline.tokenizer.model_max_length != VERY_LARGE_INTEGER:
            return
        # Only override if it's the default value:
        # i.e., VERY_LARGE_INTEGER for models that don't have a model_max_length explicity set
        # Common parameter names to check in config
        plausible_max_length_params = [
            # BERT-based, LLaMA
            "max_position_embeddings",
            # GPT-2-based
            "n_positions",
            "n_ctx",
            # ChatGLM-based
            "max_sequence_length",
            "seq_length",
            # Mistral-based
            "sliding_window",
        ]

        # Check config parameters
        for param in plausible_max_length_params:
            if hasattr(config, param):
                value = getattr(config, param)
                if isinstance(value, int) and value < VERY_LARGE_INTEGER:  # Sanity check for reasonable values
                    self._pipeline.tokenizer.model_max_length = value
                    logger.info(
                        f"Setting the maximum length of input tokens to {value} \
                                based on the config.{param} attribute."
                    )
                    return

        # If no suitable parameter is found, warn the user and continue with the HF default
        logger.warning(
            f"Could not find a suitable parameter in the model config to set model_max_length. \
                Using default value: {self._pipeline.tokenizer.model_max_length}"
        )

    def predict(self, prompt):
        # When using a text-generation model, the pipeline returns a dictionary with a single key,
        # 'generated_text'. The value of this key is a list of dictionaries, each containing the\
        # role and content of a message. For example:
        # [{'role': 'system', 'content': 'You are a helpful assistant.'},
        #  {'role': 'user', 'content': 'What is the capital of France?'}, ...]
        # We want to return the content of the last message in the list, which is the model's
        # response to the prompt.
        if self._task == "text-generation":
            messages = [
                {"role": "system", "content": self._system},
                {"role": "user", "content": prompt},
            ]
            generation = self._pipeline(messages)[0]
            return generation["generated_text"][-1]["content"]

        # If we're using a summarization model, the pipeline returns a dictionary with a single key.
        # The name of the key depends on the task (e.g., 'summary_text' for summarization).
        # Get the name of the key and return its value.
        if self._task == "summarization":
            generation = self._pipeline(prompt)[0]
            return generation["summary_text"]
