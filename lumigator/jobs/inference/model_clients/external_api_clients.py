from inference_config import InferenceJobConfig
from litellm import batch_completion
from litellm.types.utils import ModelResponse
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
        self.api_key = api_key
        self.config = config
        self.system_prompt = self.config.system_prompt
        logger.info(f"LiteLLMModelClient initialized with config: {config}")

    @retry_with_backoff(max_retries=3)
    def _make_completion_request(self, litellm_model: str, examples: list[dict[str, str]]) -> list[ModelResponse]:
        """Make a request to the LLM with proper error handling"""
        return batch_completion(
            model=litellm_model,
            messages=examples,
            max_tokens=self.config.generation_config.max_new_tokens,
            frequency_penalty=self.config.generation_config.frequency_penalty,
            temperature=self.config.generation_config.temperature,
            top_p=self.config.generation_config.top_p,
            drop_params=True,
            api_base=self.config.inference_server.base_url if self.config.inference_server else None,
            api_key=self.api_key,
        )

    def _create_prediction_result(self, response_with_index):
        index, response = response_with_index
        logger.info(response)

        # Extract and log cost. In the case of self-hosted models,
        # there is not a _hidden_params attribute in the response.
        if hasattr(response, "_hidden_params") and "response_cost" in response._hidden_params:
            cost = response._hidden_params["response_cost"]
        else:
            cost = 0
        logger.info(f"Response {index} cost {cost}")

        # Extract and log usage
        usage = response["usage"]
        logger.info(f"Response {index} usage: {usage}.")

        # Extract prediction from response
        prediction = response.choices[0].message.content

        # Check if reasoning is available in provider_specific_fields
        if response.choices[0].message.provider_specific_fields is None:
            has_reasoning_content = False
        else:
            has_reasoning_content = bool(
                response.choices[0].message.provider_specific_fields.get("reasoning_content", None)
            )
        if not has_reasoning_content:
            logger.info("No specific reasoning content found in response.")
        reasoning = response.choices[0].message.reasoning_content if has_reasoning_content else None
        if reasoning:
            logger.info("Reasoning: {reasoning}")

        # Calculate reasoning tokens
        reasoning_tokens = usage["completion_tokens_details"].reasoning_tokens if has_reasoning_content else 0

        # Handle cases where reasoning is embedded in the completion (e.g., DeepSeek R1)
        if not reasoning and "</think>" in prediction:
            logger.info(
                "You’re using a reasoning model, but the response lacks reasoning content. "
                "Trying to extract the reasoning content..."
            )
            reasoning_parts = prediction.split("</think>")
            reasoning = reasoning_parts[0].strip()
            prediction = reasoning_parts[1].strip()
            # Rough estimate of reasoning tokens
            reasoning_tokens = int(len(reasoning.split()) / 0.75)

        # Create and return prediction result
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

    def predict(self, examples: list[list[dict[str, str]]]) -> list[PredictionResult]:
        litellm_model = f"{self.config.inference_server.provider}/{self.config.inference_server.model}"
        logger.info(f"Sending request to {litellm_model}")

        responses: list = self._make_completion_request(litellm_model, examples)

        prediction_results = list(map(self._create_prediction_result, enumerate(responses)))

        return prediction_results
