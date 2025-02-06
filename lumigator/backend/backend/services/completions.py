from abc import ABC, abstractmethod

from litellm import APIError, OpenAIError, completion
from lumigator_schemas.completions import CompletionRequest, CompletionResponse

from backend.config_templates import SUPPORTED_CONFIGS
from backend.services.exceptions.completion_exceptions import CompletionUpstreamError


class CompletionService(ABC):
    @abstractmethod
    def get_completions_response(self, request: CompletionRequest) -> CompletionResponse:
        pass


class LiteLLMCompletionService(CompletionService):
    def get_completions_response(self, request: CompletionRequest) -> CompletionResponse:
        """Gets a completion response from the API.

        :param request: the request (text) to be completed
        :raises CompletionUpstreamError: if there is an exception interacting with OpenAI
        """
        model = request.model_name
        model_config = SUPPORTED_CONFIGS.get(model)
        service_name = "LiteLLM"
        if not model_config:
            raise CompletionUpstreamError(
                service_name, f"model {model} is not supported by Lumigator", None
            )
        try:
            response = completion(
                model=model_config["litellm_params"]["model"],
                messages=[
                    {"role": "system", "content": model_config["prompt"]},
                    {"role": "user", "content": request.text},
                ],
                temperature=model_config["temperature"],
                max_tokens=model_config["max_tokens"],
                top_p=model_config["top_p"],
            )
            response = response.choices[0].message.content
            return CompletionResponse(text=response)
        except APIError as e:
            raise CompletionUpstreamError(service_name, e.message, e) from e
        except OpenAIError as e:
            raise CompletionUpstreamError(
                service_name, "unexpected error getting completions response", e
            ) from e
