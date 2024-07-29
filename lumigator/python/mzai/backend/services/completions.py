from mistralai.client import MistralClient
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

    def get_completions_response(self, prompt: str) -> str:
        prompt = f"Summarize the following text: {prompt}"

        response = self.client.completion(
            model=self.model,
            prompt=prompt,
        )

        return response.choices[0].message.content


ms = MistralCompletionService()
ms.get_completions_response("testing")
