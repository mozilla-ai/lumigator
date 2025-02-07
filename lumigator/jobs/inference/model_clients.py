import re
from abc import abstractmethod

from inference_config import InferenceJobConfig
from litellm import ModelResponse, completion
from loguru import logger
from transformers import pipeline


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
    - Choose an engine name (see https://platform.openai.com/docs/models)
    - Customize the system prompt if needed

    For compatible models:
    - Works with local/remote vLLM-served models and llamafiles
    - Provide base_url and engine
    - Customize the system prompt if needed
    """

    def __init__(self, config: InferenceJobConfig):
        self.config = config
        self.system = "You are a helpful assisant., please summarize the given input."
        logger.info(f"LiteLLMModelClient initialized with config: {config}")

    def predict(
        self,
        prompt: str,
    ) -> ModelResponse:
        response = completion(
            model=self.config.inference_server.base_url,
            messages=[
                {"role": "system", "content": self.system},
                {"role": "user", "content": prompt},
            ],
            max_tokens=self.config.params.max_tokens,
            frequency_penalty=self.config.params.frequency_penalty,
            temperature=self.config.params.temperature,
            top_p=self.config.params.top_p,
            drop_params=True,
        )
        # LiteLLM gives us the cost of each API which is nice.
        # Eventually we can add this to the response object as well.
        cost = response._hidden_params["response_cost"]
        logger.info(f"Response cost: {cost}")
        return response


class HuggingFaceModelClient(BaseModelClient):
    def __init__(self, config: InferenceJobConfig):
        self._pipeline = pipeline(**config.hf_pipeline.model_dump())

    def predict(self, prompt):
        prediction = self._pipeline(prompt)[0]

        # The result is a dictionary with a single key, which name depends on the task
        # (e.g., 'summary_text' for summarization)
        # Get the name of the key and return its value
        result_key = list(prediction.keys())[0]
        return prediction[result_key]
