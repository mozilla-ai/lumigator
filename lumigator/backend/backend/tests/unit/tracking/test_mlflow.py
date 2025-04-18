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


def test_fetch_workflow_run_valid(request_mock, fake_mlflow_tracking_client):
    """Test that a valid workflow run is returned."""
    workflow_id = "valid-workflow-id"
    response_json = {
        "run": {
            "info": {
                "run_uuid": "786095e11fd34647bb0e0b6781d5ee37",  # pragma: allowlist secret
                "experiment_id": "6",
                "run_name": "Workflow_1",
                "user_id": "unknown",
                "status": "RUNNING",
                "start_time": 1741987151637,
                "artifact_uri": "s3://lumigator-storage/mlflow/6/786095e11fd34647bb0e0b6781d5ee37/artifacts",
                "lifecycle_stage": "active",
                "run_id": "786095e11fd34647bb0e0b6781d5ee37",
            },
            "data": {
                "tags": [
                    {"key": "mlflow.runName", "value": "Workflow_1"},
                    {"key": "status", "value": "created"},
                    {"key": "description", "value": "Test workflow for inf and eval"},
                    {"key": "model", "value": "hf-internal-testing/tiny-random-LlamaForCausalLM"},
                    {"key": "system_prompt", "value": "translate en to de: "},
                ]
            },
            "inputs": {},
        }
    }

    request_mock.get(f"http://mlflow.mock/api/2.0/mlflow/runs/get?run_id={workflow_id}", json=response_json)

    result = fake_mlflow_tracking_client._fetch_workflow_run(workflow_id)

    assert result is not None
    assert result.info.lifecycle_stage == "active"


def test_fetch_workflow_run_deleted(request_mock, fake_mlflow_tracking_client):
    """Test that a deleted workflow run returns None."""
    workflow_id = "deleted-workflow-id"
    # https://mlflow.org/docs/latest/api_reference/rest-api.html#run
    response_json = {
        "run": {
            "info": {
                "run_uuid": "786095e11fd34647bb0e0b6781d5ee37",  # pragma: allowlist secret
                "experiment_id": "6",
                "run_name": "Workflow_1",
                "user_id": "unknown",
                "status": "failed",
                "start_time": 1741987151637,
                "artifact_uri": "s3://lumigator-storage/mlflow/6/786095e11fd34647bb0e0b6781d5ee37/artifacts",
                "lifecycle_stage": "deleted",
                "run_id": "786095e11fd34647bb0e0b6781d5ee37",
            },
            "data": {
                "tags": [
                    {"key": "mlflow.runName", "value": "Workflow_1"},
                    {"key": "status", "value": "created"},
                    {"key": "description", "value": "Test workflow for inf and eval"},
                    {"key": "model", "value": "hf-internal-testing/tiny-random-LlamaForCausalLM"},
                    {"key": "system_prompt", "value": "translate en to de: "},
                ]
            },
            "inputs": {},
        }
    }

    request_mock.get(f"http://mlflow.mock/api/2.0/mlflow/runs/get?run_id={workflow_id}", json=response_json)

    result = fake_mlflow_tracking_client._fetch_workflow_run(workflow_id)

    assert result is None


def test_fetch_workflow_run_not_found(request_mock, fake_mlflow_tracking_client):
    """Test that a 404 error results in None."""
    workflow_id = "missing-workflow-id"

    # Response JSON must include error code from:
    # https://github.com/mlflow/mlflow/blob/4a4716324a2e736eaad73ff9dcc76ff478a29ea9/mlflow/protos/databricks_pb2.py#L74
    request_mock.get(
        f"http://mlflow.mock/api/2.0/mlflow/runs/get?run_id={workflow_id}",
        status_code=HTTPStatus.NOT_FOUND,
        json={"message": "Run not found", "error_code": "NOT_FOUND"},
    )

    result = fake_mlflow_tracking_client._fetch_workflow_run(workflow_id)

    assert result is None


def test_fetch_workflow_run_raises_exception(request_mock, fake_mlflow_tracking_client):
    """Test that any other MlflowException is raised."""
    workflow_id = "error-workflow-id"

    request_mock.get(
        f"http://mlflow.mock/api/2.0/mlflow/runs/get?run_id={workflow_id}",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        json={"message": "Some error", "error_code": "INTERNAL_ERROR"},
    )

    with pytest.raises(MlflowException, match="Some error"):
        fake_mlflow_tracking_client._fetch_workflow_run(workflow_id)


def test_get_job_ids_success(request_mock, fake_mlflow_tracking_client, json_mlflow_runs_search_single):
    """Test that job IDs are correctly returned when jobs are found."""
    workflow_id = "valid-workflow-id"
    experiment_id = "valid-experiment-id"

    # Mock the response for search_runs with jobs
    request_mock.post("http://mlflow.mock/api/2.0/mlflow/runs/search", json=json_mlflow_runs_search_single)

    result = fake_mlflow_tracking_client._get_job_ids(workflow_id, experiment_id)

    assert result == [
        "e3540cb03c994c549b327b83851cfd2a",  # pragma: allowlist secret
        "55e682b9b4d54d82b207418a57e8de46",  # pragma: allowlist secret
        "712d0ff32e22431d9bd60e95791f174d",  # pragma: allowlist secret
    ]
    assert request_mock.called


def test_get_job_ids_no_jobs(request_mock, fake_mlflow_tracking_client):
    """Test that an empty list is returned when no jobs are found."""
    workflow_id = "valid-workflow-id"
    experiment_id = "valid-experiment-id"
    response_json = {"runs": []}

    # Mock the response for search_runs with no jobs
    request_mock.post("http://mlflow.mock/api/2.0/mlflow/runs/search", json=response_json)

    result = fake_mlflow_tracking_client._get_job_ids(workflow_id, experiment_id)

    assert result == []
    assert request_mock.called


def test_get_job_ids_error(request_mock, fake_mlflow_tracking_client):
    """Test that an error results in an exception being raised."""
    workflow_id = "valid-workflow-id"
    experiment_id = "valid-experiment-id"

    # Simulate an error by returning a 500 Internal Server Error
    request_mock.post(
        "http://mlflow.mock/api/2.0/mlflow/runs/search",
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        json={"message": "Internal server error"},
    )

    with pytest.raises(Exception, match="Internal server error"):
        fake_mlflow_tracking_client._get_job_ids(workflow_id, experiment_id)

    assert request_mock.called


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
