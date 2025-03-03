from uuid import UUID

import pytest
from lumigator_schemas.tasks import SYSTEM_PROMPT_DEFAULTS
from lumigator_schemas.workflows import WorkflowCreateRequest

from backend.tests.conftest import TEST_SEQ2SEQ_MODEL


def test_workflow_request_requires_system_prompt_for_text_generation():
    # Create a text generation task definition
    task_definition = {"task": "text-generation"}

    # Test that creating a WorkflowCreateRequest without system_prompt raises an error
    with pytest.raises(ValueError) as excinfo:
        WorkflowCreateRequest(
            name="test_text_generation_run",
            description="Test missing system prompt for text generation",
            model="microsoft/Phi-3-mini-instruct",
            provider="hf",
            task_definition=task_definition,
            # system_prompt is intentionally not provided
            dataset=UUID("d34dd34d-d34d-d34d-d34d-d34dd34dd34d"),
        )

    # Verify exact error message from Pydantic validation
    assert "Default system_prompt not available for text-generation" in str(excinfo.value)


def test_default_system_prompt_for_summarization():
    # Create a WorkflowCreateRequest without specifying system_prompt
    workflow_request = WorkflowCreateRequest(
        name="test_summarization_run",
        description="Test default system prompt for summarization",
        model=TEST_SEQ2SEQ_MODEL,
        provider="hf",
        task_definition={"task": "summarization"},
        # system_prompt is intentionally not provided
        dataset=UUID("d34dd34d-d34d-d34d-d34d-d34dd34dd34d"),
    )

    # Verify that the default system prompt for summarization was applied
    expected_prompt = SYSTEM_PROMPT_DEFAULTS["summarization"]
    assert workflow_request.system_prompt == expected_prompt


def test_default_system_prompt_for_translation():
    # Create a WorkflowCreateRequest without specifying system_prompt
    workflow_request = WorkflowCreateRequest(
        name="test_translation_run",
        description="Test default system prompt for translation",
        model="hf-internal-testing/tiny-random-mt5",
        provider="hf",
        task_definition={
            "task": "translation",
            "source_language": "English",
            "target_language": "Spanish",
        },
        # system_prompt is intentionally not provided
        dataset=UUID("d34dd34d-d34d-d34d-d34d-d34dd34dd34d"),
    )

    # Verify that the default system prompt for translation was applied
    expected_prompt = "translate English to Spanish: "
    assert workflow_request.system_prompt == expected_prompt


def test_custom_system_prompt_overrides_default():
    # Create a WorkflowCreateRequest with a custom system prompt
    custom_prompt = "Create a one-sentence summary."
    workflow_request = WorkflowCreateRequest(
        name="test_custom_prompt_run",
        description="Test custom system prompt overrides default",
        model=TEST_SEQ2SEQ_MODEL,
        provider="hf",
        task_definition={"task": "summarization"},
        system_prompt=custom_prompt,  # Provide a custom system prompt
        dataset=UUID("d34dd34d-d34d-d34d-d34d-d34dd34dd34d"),
    )

    # Verify that the custom system prompt was used instead of the default
    default_summarization_prompt = SYSTEM_PROMPT_DEFAULTS["summarization"]
    assert workflow_request.system_prompt == custom_prompt
    assert workflow_request.system_prompt != default_summarization_prompt
