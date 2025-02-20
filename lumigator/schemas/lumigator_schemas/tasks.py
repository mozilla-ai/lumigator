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

    @abstractmethod
    def set_default_prompt(self, config):
        pass


class TextGenerationValidator(TaskValidator):
    def validate(self, config):
        # Validate that the system prompt is provided
        if config.system_prompt is None:
            raise ValueError("system_prompt must be provided for text generation tasks.")

    def set_default_prompt(self, config):
        # No default prompt is set, as the user is expected to provide one
        # according to the task they want to perform.
        pass


class SummarizationValidator(TaskValidator):
    DEFAULT_PROMPT: str = "You are a helpful assistant, expert in text summarization. For every prompt you receive, provide a summary of its contents in at most two sentences."  # noqa: E501

    def validate(self, config):
        if config.source_language or config.target_language:
            raise ValueError(
                f"Fields source_language and target_language should not be provided when task={TaskType.SUMMARIZATION}"
                f"but got source_language={config.source_language} and target_language={config.target_language}"
            )

    def set_default_prompt(self, config):
        # We set the default prompt only if the user has not provided one
        if config.system_prompt is None:
            config.system_prompt = self.DEFAULT_PROMPT


class TranslationValidator(TaskValidator):
    def validate(self, config):
        if not config.source_language or not config.target_language:
            raise ValueError(
                f"Both source_language and target_language must be provided when task='{TaskType.TRANSLATION},"
                f"but got source_language={config.source_language} and target_language={config.target_language}"
            )

    def set_default_prompt(self, config):
        # We set the default prompt only if the user has not provided one
        # and it is dependent on the source and target languages provided by the user
        if config.system_prompt is None:
            config.system_prompt = f"translate {config.source_language} to {config.target_language}:"
