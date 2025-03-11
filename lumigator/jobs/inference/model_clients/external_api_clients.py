from inference_config import InferenceJobConfig
from litellm import Usage, completion
from loguru import logger
from model_clients.base_client import BaseModelClient
from utils import retry_with_backoff

from schemas import InferenceMetrics, PredictionResult


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

    def __init__(self, config: InferenceJobConfig, api_key: str | None = None) -> None:
        self.config = config
        self.system_prompt = self.config.system_prompt
        self.api_key = api_key
        logger.info(f"LiteLLMModelClient initialized with config: {config}")

    @retry_with_backoff(max_retries=3)
    def _make_completion_request(self, litellm_model: str, prompt: str):
        """Make a request to the LLM with proper error handling"""
        return completion(
            model=litellm_model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=self.config.generation_config.max_new_tokens,
            frequency_penalty=self.config.generation_config.frequency_penalty,
            temperature=self.config.generation_config.temperature,
            top_p=self.config.generation_config.top_p,
            drop_params=True,
            api_base=self.config.inference_server.base_url if self.config.inference_server else None,
            api_key=self.api_key,
        )

    def predict(
        self,
        prompt: str,
    ) -> PredictionResult:
        litellm_model = f"{self.config.inference_server.provider}/{self.config.inference_server.model}"
        logger.info(f"Sending request to {litellm_model}")
        response = self._make_completion_request(litellm_model, prompt)

        # LiteLLM gives us the cost of each API which is nice.
        # Eventually we can add this to the response object as well.
        cost = response._hidden_params["response_cost"]
        logger.info(f"Response cost: {cost}")
        usage: Usage = response["usage"]
        if usage:
            logger.info(f"Usage: {usage}")
        prediction = response.choices[0].message.content
        print(response.choices[0].message)
        # LiteLLM will give us the reasoning if the API gives it back in its own field
        # When talking to llamafile, the reasoning_content key is not present
        if "reasoning_content" in response.choices[0].message.provider_specific_fields:
            reasoning = response.choices[0].message.reasoning_content
        else:
            reasoning = None
        if reasoning:
            reasoning_tokens = response["usage"]["completion_tokens_details"].reasoning_tokens
        else:
            reasoning_tokens = 0
        # In some cases (aka vLLM deployments of DeepSeek R1) the reasoning is in the completion itself
        # APIs are still catching up to adding "reasoning" as a separate field
        # since it involves post processing model output
        if not reasoning and "</think>" in prediction:
            logger.info("Reasoning found in completion")
            reasoning = prediction.split("</think>")[0].strip()
            prediction = prediction.split("</think>")[1].strip()
            # Rough estimate of reasoning tokens
            # https://www.restack.io/p/tokenization-answer-token-size-word-count-cat-ai
            reasoning_tokens = int(len(reasoning.split()) / 0.75)

        return PredictionResult(
            prediction=prediction,
            reasoning=reasoning,
            metrics=InferenceMetrics(
                prompt_tokens=usage.prompt_tokens,
                total_tokens=usage.total_tokens,
                completion_tokens=usage.completion_tokens,
                reasoning_tokens=reasoning_tokens,
                answer_tokens=usage.completion_tokens - reasoning_tokens,
            ),
        )
