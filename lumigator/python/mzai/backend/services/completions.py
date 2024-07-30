import mistralai.client
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from openai import OpenAI
from abc import ABC, abstractmethod
import os

from mzai.schemas.completions import CompletionResponse, CompletionRequest


class CompletionService(ABC):
    @abstractmethod
    def get_completions_response(self):
        pass


class MistralCompletionService(CompletionService):
    def __init__(self):
        self.client = MistralClient(api_key=os.environ["MISTRAL_API_KEY"])
        self.model = "open-mistral-7b"
        self.max_tokens = 256
        self.temperature = 1
        self.top_p = 1

    def get_models(self) -> mistralai.client.ModelList:
        response = self.client.list_models()
        return response

    def get_completions_response(self, request: CompletionRequest) -> CompletionResponse:
        response = self.client.chat(
            model=self.model,
            messages=[ChatMessage(role="user", content=f"Summarize the following: {request.text}")],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
        )
        response = response.choices[0].message.content
        return CompletionResponse(text=response)


class OpenAICompletionService(CompletionService):
    def __init__(self):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.model = "gpt-4o-mini"
        self.max_tokens = 256
        self.temperature = 1
        self.top_p = 1

    def get_models(self) -> mistralai.client.ModelList:
        response = self.client.list_models()

        return response

    def get_completions_response(self, request: CompletionRequest) -> CompletionResponse:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": f"Summarize the following: {request.text}"}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
        )
        response = response.choices[0].message.content
        return CompletionResponse(text=response)
