import pytest
from lumigator_schemas.workflows import WorkflowStatus
from mlflow.entities import RunStatus

from backend.tracking.mlflow import MLflowTrackingClient


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tracking_status, workflow_status, expected",
    [
        ("SCHEDULED", WorkflowStatus.CREATED, True),
        ("RUNNING", WorkflowStatus.RUNNING, True),
        ("FAILED", WorkflowStatus.FAILED, True),
        ("FINISHED", WorkflowStatus.SUCCEEDED, True),
        # Negative cases
        ("FAILED", WorkflowStatus.SUCCEEDED, False),
        ("RUNNING", WorkflowStatus.CREATED, False),
    ],
)
async def test_is_status_mapped_valid_and_invalid_mappings(fake_s3fs, tracking_status, workflow_status, expected):
    client = MLflowTrackingClient(tracking_uri="dummy_uri", s3_file_system=fake_s3fs)
    result = await client.is_status_match(tracking_status, workflow_status)
    assert result is expected


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_status", ["INVALID", "", None, "123"])
async def test_is_status_mapped_invalid_status_raises(fake_s3fs, invalid_status):
    client = MLflowTrackingClient(tracking_uri="dummy_uri", s3_file_system=fake_s3fs)
    with pytest.raises(ValueError, match="Status '.*' not valid."):
        await client.is_status_match(invalid_status, WorkflowStatus.RUNNING)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tracking_status,expected_terminal",
    [
        ("FINISHED", True),
        ("FAILED", True),
        ("SCHEDULED", False),
        ("RUNNING", False),
    ],
)
async def test_is_status_terminal_valid_statuses(fake_s3fs, tracking_status, expected_terminal):
    client = MLflowTrackingClient(tracking_uri="dummy_uri", s3_file_system=fake_s3fs)
    result = await client.is_status_terminal(tracking_status)
    assert result is expected_terminal


@pytest.mark.asyncio
async def test_is_status_terminal_invalid_status_string(fake_s3fs):
    client = MLflowTrackingClient(tracking_uri="dummy_uri", s3_file_system=fake_s3fs)
    with pytest.raises(ValueError, match="Status 'UNKNOWN' not valid."):
        await client.is_status_terminal("UNKNOWN")


@pytest.mark.asyncio
async def test_is_status_terminal_unmapped_status(fake_s3fs, monkeypatch):
    client = MLflowTrackingClient(tracking_uri="http://fake-tracking-uri", s3_file_system=fake_s3fs)
    with pytest.raises(ValueError, match="Status 'KILLED' not found in mapping."):
        await client.is_status_terminal(RunStatus.to_string(RunStatus.KILLED))
