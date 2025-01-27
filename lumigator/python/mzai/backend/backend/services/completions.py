from abc import ABC, abstractmethod
from http import HTTPStatus

from lumigator_schemas.completions import CompletionRequest, CompletionResponse
from mistralai.client import MistralClient
from mistralai.exceptions import MistralAPIException, MistralException
from mistralai.models.chat_completion import ChatMessage
from openai import APIError, OpenAI, OpenAIError

from backend.services.exceptions.completion_exceptions import CompletionUpstreamError
from backend.settings import settings


class CompletionService(ABC):
    @abstractmethod
    def get_completions_response(self, request: CompletionRequest) -> CompletionResponse:
        pass


class MistralCompletionService(CompletionService):
    def __init__(self):
        if settings.MISTRAL_API_KEY is None:
            raise Exception("MISTRAL_API_KEY is not set")
        self.client = MistralClient(api_key=settings.MISTRAL_API_KEY)
        self.model = "open-mistral-7b"
        self.max_tokens = 256
        self.temperature = 1
        self.top_p = 1
        self.prompt = settings.DEFAULT_SUMMARIZER_PROMPT

    def get_completions_response(self, request: CompletionRequest) -> CompletionResponse:
        """Gets a completion response from the API.

        :param request: the request (text) to be completed
        :raises CompletionUpstreamError: if there is an exception interacting with Mistral
        """
        service_name = "Mistral"
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    ChatMessage(role="system", content=f"{self.prompt}"),
                    ChatMessage(role="user", content=f"{request.text}"),
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
            )
            response = response.choices[0].message.content
            return CompletionResponse(text=response)
        except MistralAPIException as e:
            raise CompletionUpstreamError(service_name, HTTPStatus(e.http_status).phrase, e) from e
        except MistralException as e:
            raise CompletionUpstreamError(
                service_name, "unexpected error getting completions response", e
            ) from e


class OpenAICompletionService(CompletionService):
    def __init__(self):
        if settings.OAI_API_KEY is None:
            raise Exception("OPENAI_API_KEY is not set")
        self.client = OpenAI(api_key=settings.OAI_API_KEY)
        self.model = "gpt-4o-mini"
        self.max_tokens = 256
        self.temperature = 1
        self.top_p = 1
        self.prompt = settings.DEFAULT_SUMMARIZER_PROMPT

    def get_completions_response(self, request: CompletionRequest) -> CompletionResponse:
        """Gets a completion response from the API.

        :param request: the request (text) to be completed
        :raises CompletionUpstreamError: if there is an exception interacting with OpenAI
        """
        service_name = "OpenAI"
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": request.text},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
            )
            response = response.choices[0].message.content
            return CompletionResponse(text=response)
        except APIError as e:
            raise CompletionUpstreamError(service_name, e.message, e) from e
        except OpenAIError as e:
            raise CompletionUpstreamError(
                service_name, "unexpected error getting completions response", e
            ) from e
