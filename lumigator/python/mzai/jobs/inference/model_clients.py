import os
import re
from abc import abstractmethod

import torch
from asset_loader import HuggingFaceModelLoader, HuggingFaceTokenizerLoader
from inference_config import InferenceJobConfig
from loguru import logger
from mistralai.client import MistralClient
from openai import OpenAI, OpenAIError
from openai.types import Completion


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
        self._system = config.job.system_prompt

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
    """Model client for HF models (model is loaded locally, both Seq2SeqLM
    and CausalLM are supported).
    - Provide model path to load the model locally
    - Make sure you add quantization details if the model is too large
    - Optionally, add a tokenizer (the one matching the specified model name is the default)
    """

    def __init__(self, config: InferenceJobConfig):
        self._config = config
        self._device = "cuda" if torch.cuda.is_available() else "cpu"

        hf_model_loader = HuggingFaceModelLoader()
        hf_tokenizer_loader = HuggingFaceTokenizerLoader()
        self._model = hf_model_loader.load_pretrained_model(config.model).to(self._device)
        self._tokenizer = hf_tokenizer_loader.load_pretrained_tokenizer(config.tokenizer)
        self._prefix = self._get_task_specific_prefix()

    def _get_task_specific_prefix(self) -> str:
        task = self._config.job.task

        model_config = self._model.config.to_dict()
        model_config.setdefault("task_specific_params", {})

        if task in model_config["task_specific_params"]:
            prefix = model_config["task_specific_params"][task].get("prefix", "")
            if not prefix:
                logger.warning(
                    f"The model config does not include a prefix for the {task} task. "
                    f"The system prompt will be used instead."
                    f"If the system prompt is not set, the model inputs will have no prefix."
                )
                return self._config.job.system_prompt + " "
            if prefix and self._config.job.system_prompt:
                logger.warning(
                    f"The model config includes a prefix for the {task} task, "
                    f"but the job config also includes a system prompt. "
                    f"The model config prefix will be used."
                )
            return prefix

        logger.info(
            "Using system prompt as prefix. "
            "If the system prompt is not set, the model inputs will have no prefix."
        )
        return self._config.job.system_prompt + " "

    def _preprocess(self, prompt: str) -> str:
        return self._prefix + prompt

    def predict(self, prompt):
        inputs = self._tokenizer(
            self._preprocess(prompt), truncation=True, padding=True, return_tensors="pt"
        ).to(self._device)

        generated_ids = self._model.generate(**inputs, max_new_tokens=256)
        return self._tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
