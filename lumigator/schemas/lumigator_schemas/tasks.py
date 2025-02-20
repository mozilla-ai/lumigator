from abc import ABC, abstractmethod
from enum import Enum


class TaskType(str, Enum):
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    TEXT_GENERATION = "text-generation"


class TaskValidator(ABC):
    @abstractmethod
    def validate(self, config):
        pass


class TextGenerationValidator(TaskValidator):
    def validate(self, config):
        if config.source_language or config.target_language:
            raise ValueError(
                f"Fields source_language and target_language should not be provided when task={TaskType.SUMMARIZATION}"
                f"but got source_language={config.source_language} and target_language={config.target_language}"
            )


class TranslationValidator(TaskValidator):
    def validate(self, config):
        if not config.source_language or not config.target_language:
            raise ValueError(
                f"Both source_language and target_language must be provided when task='{TaskType.TRANSLATION},"
                f"but got source_language={config.source_language} and target_language={config.target_language}"
            )
