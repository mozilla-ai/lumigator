from abc import ABC, abstractmethod

import mistralai.client
from lumigator_schemas.completions import CompletionRequest, CompletionResponse
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from openai import OpenAI

from backend.settings import settings


class CompletionService(ABC):
    @abstractmethod
    def get_completions_response(self):
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

    def get_models(self) -> mistralai.client.ModelList:
        response = self.client.list_models()
        return response

    def get_completions_response(self, request: CompletionRequest) -> CompletionResponse:
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


class OpenAICompletionService(CompletionService):
    def __init__(self):
        if settings.OPENAI_API_KEY is None:
            raise Exception("OPENAI_API_KEY is not set")
        self.client = OpenAI(api_key=settings.OAI_API_KEY)
        self.model = "gpt-4o-mini"
        self.max_tokens = 256
        self.temperature = 1
        self.top_p = 1
        self.prompt = settings.DEFAULT_SUMMARIZER_PROMPT

    def get_models(self):
        """Response is stdout write
        See OpenAI Client src/openai/cli/_utils.py#L35
        """
        response = self.client.list_models()

        return response

    def get_completions_response(self, request: CompletionRequest) -> CompletionResponse:
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
