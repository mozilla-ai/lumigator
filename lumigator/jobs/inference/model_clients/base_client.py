from abc import ABC, abstractmethod

from inference_config import InferenceJobConfig

from schemas import PredictionResult


class BaseModelClient(ABC):
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
    def predict(self, examples: str | list[list[dict[str, str]]]) -> list[PredictionResult]:
        """Given a set of examples, return a set of predictions."""
        pass
