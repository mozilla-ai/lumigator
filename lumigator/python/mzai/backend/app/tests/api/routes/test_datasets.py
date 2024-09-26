import csv
import io
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


def test_upload_delete(app_client: TestClient, valid_experiment_dataset):
    upload_filename = "dataset.csv"

    # Create
    create_response = app_client.post(
        url="/datasets",
        data={"format": DatasetFormat.EXPERIMENT.value},
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


def test_presigned_download(app_client: TestClient, valid_experiment_dataset):
    upload_filename = "dataset.csv"

    # Create
    create_response = app_client.post(
        url="/datasets",
        data={"format": DatasetFormat.EXPERIMENT.value},
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


def test_experiment_format_validation(
    app_client: TestClient,
    missing_examples_dataset,
    extra_column_dataset,
):
    datasets = [missing_examples_dataset, extra_column_dataset]
    for d in datasets:
        response = app_client.post(
            url="/datasets",
            data={"format": DatasetFormat.EXPERIMENT.value},
            files={"dataset": ("dataset.csv", d)},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
