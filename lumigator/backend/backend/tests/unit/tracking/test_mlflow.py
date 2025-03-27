from http import HTTPStatus

import pytest
from lumigator_schemas.workflows import WorkflowStatus
from mlflow.entities import RunStatus
from mlflow.exceptions import MlflowException

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


@pytest.mark.parametrize(
    "overwritten, unmerged, skipped, expected_logs",
    [
        # Test case 1: Overwritten keys only
        (
            {"a", "b.c", "d.e.f", "d.e.g"},
            set(),
            set(),
            [("WARNING", "Workflow: 'wf1'. Job 'job1'. Overwritten existing keys: a, b [.c], d [.e.f, .e.g]")],
        ),
        # Test case 2: Unmerged keys only
        (
            set(),
            {"x", "y.z", "w.v.u"},
            set(),
            [("WARNING", "Workflow: 'wf1'. Job 'job1'. No data found for keys: w [.v.u], x, y [.z]")],
        ),
        # Test case 3: Skipped keys only
        (
            set(),
            set(),
            {"m", "n.o", "p.q.r"},
            [("DEBUG", "Workflow: 'wf1'. Job 'job1'. Skipped keys: m, n [.o], p [.q.r]")],
        ),
        # Test case 4: Combination of all three
        (
            {"a", "b.c"},
            {"x", "y.z"},
            {"m", "n.o"},
            [
                ("WARNING", "Workflow: 'wf1'. Job 'job1'. Overwritten existing keys: a, b [.c]"),
                ("WARNING", "Workflow: 'wf1'. Job 'job1'. No data found for keys: x, y [.z]"),
                ("DEBUG", "Workflow: 'wf1'. Job 'job1'. Skipped keys: m, n [.o]"),
            ],
        ),
        # Test case 5: Empty sets (no logging should occur)
        (
            set(),
            set(),
            set(),
            [],
        ),
    ],
)
def test_mlflow_log_key_changes(caplog_with_loguru, overwritten, unmerged, skipped, expected_logs, fake_s3fs):
    tracking_client = MLflowTrackingClient("uri", fake_s3fs)

    with caplog_with_loguru.at_level("DEBUG"):  # Capture all log levels
        tracking_client._log_key_changes("wf1", "job1", overwritten, unmerged, skipped)

    # Normalize logs by stripping extra spaces
    log_messages = [(record.levelname, record.message.strip()) for record in caplog_with_loguru.records]

    assert log_messages == expected_logs


@pytest.mark.parametrize(
    "overwritten_keys, unmerged_keys, skipped_keys, expected_warning_log, expected_debug_log",
    [
        (
            {"a", "b.c", "d.e.f", "d.e.g"},
            {"x", "y.z"},
            {"p", "q.r"},
            "Workflow: 'wf1'. Job 'job1'. Overwritten existing keys: a, b [.c], d [.e.f, .e.g]",
            "Workflow: 'wf1'. Job 'job1'. Skipped keys: p, q [.r]",
        ),
    ],
)
def test_mlflow_log_key_changes_warning_level(
    caplog_with_loguru,
    overwritten_keys,
    unmerged_keys,
    skipped_keys,
    expected_warning_log,
    expected_debug_log,
    fake_s3fs,
):
    # Set log level to WARNING (to suppress DEBUG logs)
    with caplog_with_loguru.at_level("WARNING"):
        # Instantiate the class and call the method
        tracking_client = MLflowTrackingClient("uri", fake_s3fs)
        tracking_client._log_key_changes("wf1", "job1", overwritten_keys, unmerged_keys, skipped_keys)

    # Check that the WARNING log is emitted as expected
    assert any(
        expected_warning_log in record.message and record.levelname == "WARNING"
        for record in caplog_with_loguru.records
    )

    # Check that DEBUG logs are not emitted
    assert not any(
        expected_debug_log in record.message and record.levelname == "DEBUG" for record in caplog_with_loguru.records
    )


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
