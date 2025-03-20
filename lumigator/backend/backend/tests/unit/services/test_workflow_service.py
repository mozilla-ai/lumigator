import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

from lumigator_schemas.tasks import (
    SummarizationTaskDefinition,
    TaskType,
    TextGenerationTaskDefinition,
    TranslationTaskDefinition,
)
from lumigator_schemas.workflows import WorkflowCreateRequest

from backend.services.exceptions.workflow_exceptions import WorkflowValidationError
from backend.services.workflows import WorkflowService
from backend.settings import SYSTEM_PROMPT_DEFAULTS, settings
from backend.tests.conftest import TEST_CAUSAL_MODEL, TEST_SEQ2SEQ_MODEL


def test_workflow_request_requires_system_prompt_for_text_generation(workflow_service):
    # Mock an experiment with text generation task
    experiment_mock = MagicMock()
    experiment_mock.task_definition = TextGenerationTaskDefinition()
    experiment_mock.name = "Test Experiment"

    # Configure tracking client to return our mock experiment
    workflow_service._tracking_client.get_experiment = AsyncMock(return_value=experiment_mock)

    # Create request without system prompt
    request = WorkflowCreateRequest(
        name="Test Workflow",
        experiment_id="cced289c-f869-4af1-9195-1d58e32d1cc1",
        # Add other required fields here
        model=TEST_CAUSAL_MODEL,
        provider="hf",
    )

    # Act & Assert
    with unittest.TestCase().assertRaises(WorkflowValidationError) as context:
        asyncio.run(workflow_service.create_workflow(request))

    # Verify the error message
    assert str(context.exception) == "Default system_prompt not available for text-generation"

    # Verify the experiment was retrieved
    workflow_service._tracking_client.get_experiment.assert_called_once_with(request.experiment_id)


def test_default_system_prompt_for_summarization():
    task_definition = SummarizationTaskDefinition()
    default_system_prompt = settings.get_default_system_prompt(task_definition)

    # Verify that the default system prompt for summarization was applied
    expected_prompt = SYSTEM_PROMPT_DEFAULTS["summarization"]
    assert default_system_prompt == expected_prompt


def test_default_system_prompt_for_translation():
    src_lang = "English"
    tgt_lang = "Spanish"

    task_definition = TranslationTaskDefinition(
        source_language=src_lang,
        target_language=tgt_lang,
    )
    default_system_prompt = settings.get_default_system_prompt(task_definition)

    # Verify that the default system prompt for translation was applied
    expected_prompt = (
        f"You are a helpful assistant, expert in text translation. "
        f"For every prompt you recieve, translate {src_lang} to {tgt_lang}."
    )
    assert default_system_prompt == expected_prompt


def test_custom_system_prompt_overrides_default():
    # Create a WorkflowCreateRequest with a custom system prompt
    task_definition = SummarizationTaskDefinition()
    default_system_prompt = settings.get_default_system_prompt(task_definition)
    custom_prompt = "Create a one-sentence summary."

    workflow_request = WorkflowCreateRequest(
        name="test_custom_prompt_run",
        description="Test custom system prompt overrides default",
        model=TEST_SEQ2SEQ_MODEL,
        provider="hf",
        system_prompt=custom_prompt,  # Provide a custom system prompt
        dataset=UUID("d34dd34d-d34d-d34d-d34d-d34dd34dd34d"),
    )

    # Verify that the custom system prompt was used instead of the default
    assert workflow_request.system_prompt == custom_prompt
    assert workflow_request.system_prompt != default_system_prompt
