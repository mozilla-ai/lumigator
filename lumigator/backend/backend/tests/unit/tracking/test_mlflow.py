import uuid
from unittest.mock import MagicMock

import pytest
from lumigator_schemas.jobs import JobResults
from mlflow.entities import Metric, Param, Run, RunData, RunInfo, RunTag

from backend.services.exceptions.tracking_exceptions import RunNotFoundError


def test_get_job_success(fake_mlflow_tracking_client, sample_mlflow_run):
    """Test fetching job results successfully."""
    job_id = uuid.UUID("d34dbeef-1000-0000-0000-000000000000")

    fake_mlflow_tracking_client._client.get_run = MagicMock(return_value=sample_mlflow_run)

    result = fake_mlflow_tracking_client.get_job(str(job_id))

    assert isinstance(result, JobResults)
    assert result.id == job_id
    assert result.metrics == [{"name": "accuracy", "value": 0.75}]
    assert result.parameters == [{"name": "batch_size", "value": "32"}]

    fake_mlflow_tracking_client._client.get_run.assert_called_once_with(str(job_id))


def test_get_job_deleted(fake_mlflow_tracking_client, fake_mlflow_run_deleted):
    """Test fetching a deleted job returns None."""
    job_id = uuid.UUID("d34dbeef-1000-0000-0000-000000000000")

    fake_mlflow_tracking_client._client.get_run = MagicMock(return_value=fake_mlflow_run_deleted)

    with pytest.raises(RunNotFoundError):
        fake_mlflow_tracking_client.get_job(str(job_id))

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


def test_compile_parameters(fake_mlflow_tracking_client):
    """Test parameter compilation across multiple job runs."""
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
                params=[Param(key="learning_rate", value="5")],
                tags=[
                    RunTag(key="mlflow.runName", value="Run2"),
                ],
            ),
        ),
    }

    fake_mlflow_tracking_client._client.get_run = MagicMock(side_effect=lambda job_id: runs[job_id])

    result = fake_mlflow_tracking_client._compile_parameters([job_id for job_id in job_ids.values()])

    assert result == {
        "other_thing": {
            "value": "0.01",
            "jobs": {
                "Run1": "0.01",
            },
        },
        "learning_rate": {
            "value": "5",
            "jobs": {
                "Run2": "5",
            },
        },
    }


def test_compile_parameters_conflict(fake_mlflow_tracking_client):
    """Test parameter conflicts result in no 'value' key being set."""
    job_ids = {
        "job1": "d34dbeef-1000-0000-0000-000000000001",
        "job2": "d34dbeef-1000-0000-0000-000000000002",
        "job3": "d34dbeef-1000-0000-0000-000000000003",
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
                params=[Param(key="other_thing", value="0.01"), Param(key="learning_rate", value="7")],
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
                params=[Param(key="learning_rate", value="5")],
                tags=[
                    RunTag(key="mlflow.runName", value="Run2"),
                ],
            ),
        ),
        job_ids["job3"]: Run(
            run_info=RunInfo(
                run_uuid=job_ids["job3"],
                experiment_id="exp-1",
                user_id="user",
                status="FINISHED",
                start_time=123456789,
                end_time=None,
                lifecycle_stage="active",
            ),
            run_data=RunData(
                params=[Param(key="learning_rate", value="8")],
                tags=[
                    RunTag(key="mlflow.runName", value="Run3"),
                ],
            ),
        ),
    }

    fake_mlflow_tracking_client._client.get_run = MagicMock(side_effect=lambda job_id: runs[job_id])

    result = fake_mlflow_tracking_client._compile_parameters([job_id for job_id in job_ids.values()])

    assert result == {
        "other_thing": {
            "value": "0.01",
            "jobs": {
                "Run1": "0.01",
            },
        },
        "learning_rate": {
            "jobs": {
                "Run1": "7",
                "Run2": "5",
                "Run3": "8",
            },
        },
    }
