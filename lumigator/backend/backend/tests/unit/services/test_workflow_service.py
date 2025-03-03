from uuid import UUID

import pytest
from lumigator_schemas.workflows import WorkflowCreateRequest


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
