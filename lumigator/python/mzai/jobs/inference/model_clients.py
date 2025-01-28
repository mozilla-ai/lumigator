import os
import re
from abc import abstractmethod

from inference_config import AutoTokenizerConfig, InferenceJobConfig
from loguru import logger
from mistralai.client import MistralClient
from openai import OpenAI, OpenAIError
from openai.types import Completion
from transformers import AutoTokenizer, pipeline


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


class APIModelClient(BaseModelClient):
    """General model client for APIs."""

    def __init__(self, config: InferenceJobConfig):
        self._config = config
        self._engine = strip_path_prefix(config.inference_server.engine)
        self._system = config.inference_server.system_prompt

    @abstractmethod
    def _chat_completion(
        self,
        config: InferenceJobConfig,
        client: OpenAI | MistralClient,
        prompt: str,
        system: str,
    ) -> Completion:
        """Connects to the API and returns a chat completion holding the model's response."""
        pass

    def _get_response_with_retries(
        self,
        config: InferenceJobConfig,
        prompt: str,
    ) -> tuple[str, str]:
        current_retry_attempt = 1
        max_retries = (
            1
            if config.inference_server.max_retries is None
            else config.inference_server.max_retries
        )
        while current_retry_attempt <= max_retries:
            try:
                response = self._chat_completion(self._config, self._client, prompt, self._system)
                break
            except OpenAIError as e:
                logger.warning(f"{e.message}: Retrying ({current_retry_attempt}/{max_retries})")
                current_retry_attempt += 1
                if current_retry_attempt > max_retries:
                    raise e
        return response

    def predict(self, prompt):
        response = self._get_response_with_retries(self._config, prompt)

        return response.choices[0].message.content


class OpenAIModelClient(APIModelClient):
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

    def __init__(self, base_url: str, config: InferenceJobConfig):
        super().__init__(config)
        self._client = OpenAI(base_url=base_url)

    def _chat_completion(
        self,
        config: InferenceJobConfig,
        client: OpenAI,
        prompt: str,
        system: str = "You are a helpful assisant.",
    ) -> Completion:
        """Connects to a remote OpenAI-API-compatible endpoint
        and returns a chat completion holding the model's response.
        """
        return client.chat.completions.create(
            model=self._engine,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            max_tokens=config.params.max_tokens,
            frequency_penalty=config.params.frequency_penalty,
            temperature=config.params.temperature,
            top_p=config.params.top_p,
        )


class MistralModelClient(APIModelClient):
    """Model client for models served via Mistral API.
    - The base_url is fixed
    - Choose an engine name (see https://docs.mistral.ai/getting-started/models/)
    - Customize the system prompt if needed
    """

    def __init__(self, base_url: str, config: InferenceJobConfig):
        super().__init__(config)
        self._client = MistralClient(api_key=os.environ["MISTRAL_API_KEY"])

    def _chat_completion(
        self,
        config: InferenceJobConfig,
        client: MistralClient,
        prompt: str,
        system: str = "You are a helpful assisant.",
    ) -> Completion:
        """Connects to a Mistral endpoint
        and returns a chat completion holding the model's response.
        """
        return client.chat(
            model=self._engine,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            max_tokens=config.params.max_tokens,
            temperature=config.params.temperature,
            top_p=config.params.top_p,
        )


class HuggingFaceModelClient(BaseModelClient):
    def __init__(self, config: InferenceJobConfig):
        pipeline_kwargs = config.hf_pipeline.model_dump()
        if hasattr(config.hf_pipeline, "tokenizer") and config.hf_pipeline.tokenizer:
            # If a tokenizer config is provided and is not None, load the tokenizer separately
            pipeline_kwargs["tokenizer"] = self._load_tokenizer(config.hf_pipeline.tokenizer)

        self._pipeline = pipeline(**pipeline_kwargs)

    def _load_tokenizer(self, tokenizer_config: AutoTokenizerConfig):
        logger.info(f"Loading Tokenizer with config: {tokenizer_config}")
        return AutoTokenizer.from_pretrained(**tokenizer_config.model_dump())

    def predict(self, prompt):
        prediction = self._pipeline(prompt)[0]

        # The result is a dictionary with a single key, which name depends on the task
        # (e.g., 'summary_text' for summarization)
        # Get the name of the key and return its value
        result_key = list(prediction.keys())[0]
        return prediction[result_key]
