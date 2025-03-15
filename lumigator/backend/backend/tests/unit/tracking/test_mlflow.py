from collections import defaultdict
from unittest.mock import MagicMock

import pytest
from conftest import boto_s3_client
from loguru import logger
from pyarrow._s3fs import S3FileSystem

from backend.tracking.mlflow import MLflowTrackingClient


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
def test_mlflow_log_key_changes(caplog, overwritten, unmerged, skipped, expected_logs, fake_s3fs, fake_s3_client):
    tracking_client = MLflowTrackingClient("uri", fake_s3fs, fake_s3_client)

    with caplog.at_level("DEBUG"):  # Capture all log levels
        tracking_client._log_key_changes("wf1", "job1", overwritten, unmerged, skipped)

    # Normalize logs by stripping extra spaces
    log_messages = [(record.levelname, record.message.strip()) for record in caplog.records]

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
    caplog,
    overwritten_keys,
    unmerged_keys,
    skipped_keys,
    expected_warning_log,
    expected_debug_log,
    fake_s3fs,
    fake_s3_client,
):
    # Set log level to WARNING (to suppress DEBUG logs)
    with caplog.at_level("WARNING"):
        # Instantiate the class and call the method
        tracking_client = MLflowTrackingClient("uri", fake_s3fs, fake_s3_client)
        tracking_client._log_key_changes("wf1", "job1", overwritten_keys, unmerged_keys, skipped_keys)

    # Check that the WARNING log is emitted as expected
    assert any(expected_warning_log in record.message and record.levelname == "WARNING" for record in caplog.records)

    # Check that DEBUG logs are not emitted
    assert not any(expected_debug_log in record.message and record.levelname == "DEBUG" for record in caplog.records)
