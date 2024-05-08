import csv
import io
from urllib.parse import urlparse

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from mzai.schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse


@pytest.fixture
def experiment_dataset() -> io.BytesIO:
    str_obj = io.StringIO()
    data = [["input", "target"], ["Hello World", "Hello"]]
    csv.writer(str_obj).writerows(data)
    return io.BytesIO(str_obj.read().encode("utf-8"))


def test_upload_delete(app_client: TestClient, experiment_dataset):
    upload_filename = "dataset.csv"

    # Create
    create_response = app_client.post(
        url="/datasets",
        data={"format": DatasetFormat.EXPERIMENT.value},
        files={"dataset": (upload_filename, experiment_dataset)},
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


def test_presigned_download(app_client: TestClient, experiment_dataset):
    upload_filename = "dataset.csv"

    # Create
    create_response = app_client.post(
        url="/datasets",
        data={"format": DatasetFormat.EXPERIMENT.value},
        files={"dataset": (upload_filename, experiment_dataset)},
    )
    created_dataset = DatasetResponse.model_validate(create_response.json())

    # Get download
    download_response = app_client.get(f"/datasets/{created_dataset.id}/download")
    assert download_response.status_code == status.HTTP_200_OK

    download_model = DatasetDownloadResponse.model_validate(download_response.json())
    assert download_model.id == created_dataset.id

    # Original filename is included in the presigned download URL
    # (not as a content disposition header)
    parse_result = urlparse(download_model.download_url)
    assert parse_result.path.endswith(upload_filename)
