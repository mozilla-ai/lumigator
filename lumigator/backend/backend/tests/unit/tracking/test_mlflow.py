import uuid
from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock

import pytest
from lumigator_schemas.jobs import JobResults
from lumigator_schemas.workflows import WorkflowStatus
from mlflow.entities import Metric, Param, Run, RunData, RunInfo, RunStatus, RunTag
from mlflow.exceptions import MlflowException

from backend.services.exceptions.tracking_exceptions import RunNotFoundError
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


async def test_get_job_success(fake_mlflow_tracking_client, sample_mlflow_run):
    """Test fetching job results successfully."""
    job_id = uuid.UUID("d34dbeef-1000-0000-0000-000000000000")

    fake_mlflow_tracking_client._client.get_run = MagicMock(return_value=sample_mlflow_run)

    result = await fake_mlflow_tracking_client.get_job(str(job_id))

    assert isinstance(result, JobResults)
    assert result.id == job_id
    assert result.metrics == [{"name": "accuracy", "value": 0.75}]
    assert result.parameters == [{"name": "batch_size", "value": "32"}]

    fake_mlflow_tracking_client._client.get_run.assert_called_once_with(str(job_id))


async def test_get_job_deleted(fake_mlflow_tracking_client, fake_mlflow_run_deleted):
    """Test fetching a deleted job returns None."""
    job_id = uuid.UUID("d34dbeef-1000-0000-0000-000000000000")

    fake_mlflow_tracking_client._client.get_run = MagicMock(return_value=fake_mlflow_run_deleted)

    with pytest.raises(RunNotFoundError):
        await fake_mlflow_tracking_client.get_job(str(job_id))

    fake_mlflow_tracking_client._client.get_run.assert_called_once_with(str(job_id))


def test_compile_metrics(fake_mlflow_tracking_client):
    """Test metric compilation across multiple job runs."""
    job_ids = {
        "job1": "d34dbeef-1000-0000-0000-000000000001",
        "job2": "d34dbeef-1000-0000-0000-000000000002",
    }
    runs = {
        job_ids["job1"]: Run(
            run_info=RunInfo(
                run_uuid=job_ids["job1"],
                experiment_id="exp-1",
                user_id="user",
                status="FINISHED",
                start_time=123456789,
                end_time=None,
                lifecycle_stage="active",
            ),
            run_data=RunData(
                metrics=[Metric(key="accuracy", value=0.95, timestamp=123456789, step=0)],
                params=[Param(key="other_thing", value="0.01")],
                tags=[
                    RunTag(key="mlflow.runName", value="Run1"),
                ],
            ),
        ),
        job_ids["job2"]: Run(
            run_info=RunInfo(
                run_uuid=job_ids["job2"],
                experiment_id="exp-1",
                user_id="user",
                status="FINISHED",
                start_time=123456789,
                end_time=None,
                lifecycle_stage="active",
            ),
            run_data=RunData(
                metrics=[Metric(key="loss", value=0.2, timestamp=123456789, step=0)],
                params=[Param(key="learning_rate", value="0.02")],
                tags=[
                    RunTag(key="mlflow.runName", value="Run2"),
                ],
            ),
        ),
    }

    fake_mlflow_tracking_client._client.get_run = MagicMock(side_effect=lambda job_id: runs[job_id])

    result = fake_mlflow_tracking_client._compile_metrics([job_id for job_id in job_ids.values()])

    assert result == {"loss": 0.2, "accuracy": 0.95}
    fake_mlflow_tracking_client._client.get_run.assert_any_call(job_ids["job1"])
    fake_mlflow_tracking_client._client.get_run.assert_any_call(job_ids["job2"])


def test_compile_metrics_conflict(fake_mlflow_tracking_client):
    """Test metric conflict across job runs raises assertion error."""
    job_ids = {
        "job1": "d34dbeef-1000-0000-0000-000000000001",
        "job2": "d34dbeef-1000-0000-0000-000000000002",
    }
    runs = {
        job_ids["job1"]: Run(
            run_info=RunInfo(
                run_uuid=job_ids["job1"],
                experiment_id="exp-1",
                user_id="user",
                status="FINISHED",
                start_time=123456789,
                end_time=None,
                lifecycle_stage="active",
                artifact_uri="",
            ),
            run_data=RunData(
                metrics=[Metric(key="accuracy", value=0.95, timestamp=123456789, step=0)],
                params=[Param(key="other_thing", value="0.01")],
                tags=[
                    RunTag(key="description", value="A sample workflow"),
                    RunTag(key="mlflow.runName", value="Run1"),
                    RunTag(key="model", value="SampleModel"),
                    RunTag(key="system_prompt", value="Prompt text"),
                    RunTag(key="status", value="COMPLETED"),
                ],
            ),
        ),
        job_ids["job2"]: Run(
            run_info=RunInfo(
                run_uuid=job_ids["job2"],
                experiment_id="exp-1",
                user_id="user",
                status="FINISHED",
                start_time=123456789,
                end_time=None,
                lifecycle_stage="active",
                artifact_uri="",
            ),
            run_data=RunData(
                metrics=[Metric(key="accuracy", value=0.75, timestamp=123456789, step=0)],
                params=[Param(key="learning_rate", value="0.02")],
                tags=[
                    RunTag(key="description", value="A sample workflow"),
                    RunTag(key="mlflow.runName", value="Run2"),
                    RunTag(key="model", value="SampleModel"),
                    RunTag(key="system_prompt", value="Prompt text"),
                    RunTag(key="status", value="COMPLETED"),
                ],
            ),
        ),
    }

    fake_mlflow_tracking_client._client.get_run = MagicMock(side_effect=lambda job_id: runs[job_id])

    with pytest.raises(ValueError) as e:
        fake_mlflow_tracking_client._compile_metrics([job_id for job_id in job_ids.values()])

    assert str(e.value) == (
        "Duplicate metric 'accuracy' found in job 'd34dbeef-1000-0000-0000-000000000002'. "
        "Stored value: 0.95, this value: 0.75"
    )
