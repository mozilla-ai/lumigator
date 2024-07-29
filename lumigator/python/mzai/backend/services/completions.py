import mistralai.client
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from abc import ABC, abstractmethod
import os


class CompletionService(ABC):
    @abstractmethod
    def get_completions_response(self):
        pass


class MistralCompletionService(CompletionService):
    def __init__(self):
        self.client = MistralClient(api_key=os.environ["MISTRAL_API_KEY"])
        self.model = "open-mistral-7b"
        self.max_tokens = 256
        self.temperature = 0.7
        self.top_p = 1

    def get_models(self) -> mistralai.client.ModelList:
        response = self.client.list_models()

        return response

    def get_completions_response(self, prompt: str) -> str:
        prompt = f"Summarize the following text: {prompt}"

        response = self.client.chat(
            model=self.model,
            messages=[ChatMessage(role="user", content=f"Summarize the following: {prompt}")],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
        )
        return response.choices[0].message.content
