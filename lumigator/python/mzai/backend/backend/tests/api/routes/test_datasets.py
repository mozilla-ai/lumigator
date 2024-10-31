import csv
import io
import uuid
from unittest.mock import patch
from urllib.parse import urlparse

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse


def format_dataset(data: list[list[str]]) -> str:
    """Format a list of tabular data as a CSV string."""
    buffer = io.StringIO()
    csv.writer(buffer).writerows(data)
    buffer.seek(0)
    return buffer.read()


@pytest.fixture
def valid_experiment_dataset() -> str:
    data = [
        ["examples", "ground_truth"],
        ["Hello World", "Hello"],
    ]
    return format_dataset(data)


@pytest.fixture
def valid_experiment_dataset_without_gt() -> str:
    data = [
        ["examples"],
        ["Hello World"],
    ]
    return format_dataset(data)


@pytest.fixture
def missing_examples_dataset() -> str:
    data = [
        ["ground_truth"],
        ["Hello"],
    ]
    return format_dataset(data)


@pytest.fixture
def extra_column_dataset() -> str:
    data = [
        ["examples", "ground_truth", "extra"],
        ["Hello World", "Hello", "Nope"],
    ]
    return format_dataset(data)


def test_upload_delete(app_client: TestClient, valid_experiment_dataset: str):
    upload_filename = "dataset.csv"

    # Create
    create_response = app_client.post(
        url="/datasets",
        data={"format": DatasetFormat.JOB.value},
        files={"dataset": (upload_filename, valid_experiment_dataset)},
    )
    assert create_response.status_code == status.HTTP_201_CREATED

    created_dataset = DatasetResponse.model_validate(create_response.json())
    assert created_dataset.filename == upload_filename

    # Get
    get_response = app_client.get(f"/datasets/{created_dataset.id}")
    assert get_response.status_code == status.HTTP_200_OK

    retrieved_dataset = DatasetResponse.model_validate(get_response.json())
    assert retrieved_dataset.id == created_dataset.id
    assert retrieved_dataset.filename == upload_filename

    # Delete
    delete_response = app_client.delete(f"/datasets/{created_dataset.id}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # Get after delete (not found)
    get_response = app_client.get(f"/datasets/{created_dataset.id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_dataset_delete_error(app_client: TestClient):
    dataset_id = uuid.uuid4()
    with patch(
            "backend.services.datasets.DatasetService.delete_dataset",
            side_effect=Exception("argh I am exceptional")):
        resp = app_client.delete(f"/datasets/{dataset_id}")
        assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = resp.json()
        assert data["detail"] == f"Unexpected error deleting dataset for ID: {dataset_id}"


def test_presigned_download(app_client: TestClient, valid_experiment_dataset: str):
    upload_filename = "dataset.csv"

    # Create
    create_response = app_client.post(
        url="/datasets",
        data={"format": DatasetFormat.JOB.value},
        files={"dataset": (upload_filename, valid_experiment_dataset)},
    )
    created_dataset = DatasetResponse.model_validate(create_response.json())

    # Get download
    download_response = app_client.get(f"/datasets/{created_dataset.id}/download")
    assert download_response.status_code == status.HTTP_200_OK

    download_model = DatasetDownloadResponse.model_validate(download_response.json())
    assert download_model.id == created_dataset.id

    # Original filename is included in all the presigned download URLs
    # (not as a content disposition header)
    for download_url in download_model.download_urls:
        parse_result = urlparse(download_url)
        assert upload_filename in parse_result.path


@pytest.mark.parametrize(
    "dataset, expected_status",
    [
        ("missing_examples_dataset", status.HTTP_403_FORBIDDEN),
        ("extra_column_dataset", status.HTTP_403_FORBIDDEN),
    ],
)
def test_experiment_format_validation(
    app_client: TestClient,
    dataset: str,
    expected_status: int,
):
    response = app_client.post(
        url="/datasets",
        data={"format": DatasetFormat.JOB.value},
        files={"dataset": ("dataset.csv", dataset)},
    )
    assert response.status_code == expected_status


def test_experiment_ground_truth(
    app_client: TestClient,
    valid_experiment_dataset: str,
    valid_experiment_dataset_without_gt: str,
):
    create_response = app_client.post(
        url="/datasets",
        data={"format": DatasetFormat.JOB.value},
        files={"dataset": ("dataset.csv", valid_experiment_dataset)},
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    created_dataset = DatasetResponse.model_validate(create_response.json())
    assert created_dataset.ground_truth is True

    create_response = app_client.post(
        url="/datasets",
        data={"format": DatasetFormat.JOB.value},
        files={"dataset": ("dataset.csv", valid_experiment_dataset_without_gt)},
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    created_dataset = DatasetResponse.model_validate(create_response.json())
    assert created_dataset.ground_truth is False
