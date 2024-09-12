import os
from abc import abstractmethod

import torch
from loguru import logger
from mistralai.client import MistralClient
from openai import OpenAI, OpenAIError
from openai.types import Completion
from transformers import pipeline

from lm_buddy.configs.common import LMBuddyConfig
from lm_buddy.configs.jobs.hf_evaluate import HuggingFaceEvalJobConfig
from lm_buddy.configs.vllm import VLLMCompletionsConfig
from lm_buddy.jobs.asset_loader import HuggingFaceModelLoader, HuggingFaceTokenizerLoader


class BaseModelClient:
    """
    Abstract class for a model client, used to provide a uniform interface
    (currentnly just a simple predict method) to models served in different
    ways (e.g. HF models loaded locally, OpenAI endpoints, vLLM inference
    servers, llamafile).
    """

    @abstractmethod
    def __init__(self, model: str, config: LMBuddyConfig):
        """
        Used to initialize the model / inference service.
        """
        pass

    @abstractmethod
    def predict(self, prompt: str) -> str:
        """
        Given a prompt, return a prediction.
        """
        pass


class SummarizationPipelineModelClient(BaseModelClient):
    """
    Model client for the huggingface summarization pipeline
    (model is loaded locally).
    """

    def __init__(self, model: str, config: HuggingFaceEvalJobConfig):
        self._config = config

        hf_tokenizer_loader = HuggingFaceTokenizerLoader()
        self._tokenizer = hf_tokenizer_loader.load_pretrained_tokenizer(config.tokenizer)

        self._summarizer = pipeline(
            "summarization",
            model=model,
            tokenizer=self._tokenizer,
            device=0 if torch.cuda.is_available() else -1,
            truncation=True,
        )

    def predict(self, prompt):
        # summarizer output is a list (1 element in this case) of dict with key = "summary_text"
        # TODO: bring summarizer parameters out at some point (not needed at the moment)
        pred = self._summarizer(prompt, min_length=30, do_sample=False)
        return pred[0]["summary_text"]


class HuggingFaceModelClient(BaseModelClient):
    """
    Model client for HF models (model is loaded locally, both Seq2SeqLM
    and CausalLM are supported).
    - Provide model path to load the model locally
    - Make sure you add quantization details if the model is too large
    - Optionally, add a tokenizer (the one matching the specified model name is the default)
    """

    def __init__(self, model: str, config: HuggingFaceEvalJobConfig):
        self._config = config
        self._device = "cuda" if torch.cuda.is_available() else "cpu"

        hf_model_loader = HuggingFaceModelLoader()
        hf_tokenizer_loader = HuggingFaceTokenizerLoader()
        self._model = hf_model_loader.load_pretrained_model(config.model).to(self._device)
        self._tokenizer = hf_tokenizer_loader.load_pretrained_tokenizer(config.tokenizer)

    def predict(self, prompt):
        inputs = self._tokenizer(prompt, truncation=True, padding=True, return_tensors="pt").to(
            self._device
        )
        generated_ids = self._model.generate(**inputs, max_new_tokens=256)
        return self._tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]


class APIModelClient(BaseModelClient):
    """General model client for APIs."""

    def __init__(self, config: VLLMCompletionsConfig):
        self._config = config

        hf_model_loader = HuggingFaceModelLoader()
        self._engine = hf_model_loader.resolve_asset_path(config.inference.engine)
        self._system = config.inference.system_prompt

    @abstractmethod
    def _chat_completion(
        self,
        config: VLLMCompletionsConfig,
        client: OpenAI | MistralClient,
        prompt: str,
        system: str,
    ) -> Completion:
        """Connects to the API and returns a chat completion holding the model's response."""
        pass

    def _get_response_with_retries(
        self,
        config: VLLMCompletionsConfig,
        prompt: str,
    ) -> tuple[str, str]:
        current_retry_attempt = 1
        max_retries = 1 if config.inference.max_retries is None else config.inference.max_retries
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
    """
    Model client for models served via openai-compatible API.
    For OpenAI models:
    - The base_url is fixed
    - Choose an engine name (see https://platform.openai.com/docs/models)
    - Customize the system prompt if needed

    For compatible models:
    - Works with local/remote vLLM-served models and llamafiles
    - Provide base_url and engine
    - Customize the system prompt if needed
    """

    def __init__(self, model: str, config: VLLMCompletionsConfig):
        super().__init__(config)
        self._client = OpenAI(base_url=model)

    def _chat_completion(
        self,
        config: VLLMCompletionsConfig,
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
            max_tokens=config.max_tokens,
            frequency_penalty=config.frequency_penalty,
            temperature=config.temperature,
            top_p=config.top_p,
        )


class MistralModelClient(APIModelClient):
    """
    Model client for models served via Mistral API.
    - The base_url is fixed
    - Choose an engine name (see https://docs.mistral.ai/getting-started/models/)
    - Customize the system prompt if needed
    """

    def __init__(self, model: str, config: VLLMCompletionsConfig):
        super().__init__(config)
        self._client = MistralClient(api_key=os.environ["MISTRAL_API_KEY"])

    def _chat_completion(
        self,
        config: VLLMCompletionsConfig,
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
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            top_p=config.top_p,
        )
