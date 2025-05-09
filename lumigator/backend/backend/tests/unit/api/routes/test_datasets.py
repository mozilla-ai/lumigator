import uuid
from unittest.mock import patch
from urllib.parse import urlparse

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from lumigator_schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse

from backend.api.http_headers import HttpHeaders
from backend.services.exceptions.dataset_exceptions import DatasetUpstreamError


def test_upload_delete(test_client: TestClient, valid_experiment_dataset: str, dependency_overrides_fakes):
    upload_filename = "dataset.csv"

    # Create
    create_response = test_client.post(
        url="/datasets",
        data={"format": DatasetFormat.JOB.value},
        files={"dataset": (upload_filename, valid_experiment_dataset)},
    )
    assert create_response.status_code == status.HTTP_201_CREATED

    created_dataset = DatasetResponse.model_validate(create_response.json())
    assert created_dataset.filename == upload_filename

    # Get
    get_response = test_client.get(f"/datasets/{created_dataset.id}")
    assert get_response.status_code == status.HTTP_200_OK

    retrieved_dataset = DatasetResponse.model_validate(get_response.json())
    assert retrieved_dataset.id == created_dataset.id
    assert retrieved_dataset.filename == upload_filename

    # Delete
    delete_response = test_client.delete(f"/datasets/{created_dataset.id}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # Get after delete (not found)
    get_response = test_client.get(f"/datasets/{created_dataset.id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_dataset_delete_error(test_client: TestClient, dependency_overrides_fakes):
    dataset_id = uuid.uuid4()
    msg = f"error attempting to delete dataset {dataset_id} from S3"
    with patch(
        "backend.services.datasets.DatasetService.delete_dataset",
        side_effect=DatasetUpstreamError("s3", msg),
    ):
        resp = test_client.delete(f"/datasets/{dataset_id}")
        assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = resp.json()
        assert data["detail"] == f"Upstream error with s3: {msg}"


def test_presigned_download(test_client: TestClient, valid_experiment_dataset: str, dependency_overrides_fakes):
    upload_filename = "dataset.csv"

    # Create
    create_response = test_client.post(
        url="/datasets",
        data={"format": DatasetFormat.JOB.value},
        files={"dataset": (upload_filename, valid_experiment_dataset)},
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    created_dataset = DatasetResponse.model_validate(create_response.json())

    # Get download
    download_response = test_client.get(f"/datasets/{created_dataset.id}/download")
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
        # FIXME: maybe bad request????
        ("missing_examples_dataset", status.HTTP_403_FORBIDDEN),
        ("extra_column_dataset", status.HTTP_403_FORBIDDEN),
    ],
)
def test_experiment_format_validation(
    test_client: TestClient, dataset: str, expected_status: int, dependency_overrides_fakes
):
    response = test_client.post(
        url="/datasets",
        data={"format": DatasetFormat.JOB.value},
        files={"dataset": ("dataset.csv", dataset)},
    )
    assert response.status_code == expected_status


def test_experiment_ground_truth(
    test_client: TestClient,
    valid_experiment_dataset: str,
    valid_experiment_dataset_without_gt: str,
    valid_experiment_dataset_with_empty_gt: str,
    dependency_overrides_fakes,
):
    ground_truth_response = test_client.post(
        url="/datasets",
        data={"format": DatasetFormat.JOB.value},
        files={"dataset": ("dataset.csv", valid_experiment_dataset)},
    )
    assert ground_truth_response.status_code == status.HTTP_201_CREATED
    created_dataset = DatasetResponse.model_validate(ground_truth_response.json())
    assert created_dataset.ground_truth is True
    location = ground_truth_response.headers.get(HttpHeaders.LOCATION)
    assert location != ""
    assert location == f"{test_client.base_url}datasets/{created_dataset.id}"

    no_ground_truth_response = test_client.post(
        url="/datasets",
        data={"format": DatasetFormat.JOB.value},
        files={"dataset": ("dataset.csv", valid_experiment_dataset_without_gt)},
    )
    assert no_ground_truth_response.status_code == status.HTTP_201_CREATED
    created_dataset = DatasetResponse.model_validate(no_ground_truth_response.json())
    assert created_dataset.ground_truth is False
    location = no_ground_truth_response.headers.get(HttpHeaders.LOCATION)
    assert location != ""
    assert location == f"{test_client.base_url}datasets/{created_dataset.id}"

    empty_ground_truth_response = test_client.post(
        url="/datasets",
        data={"format": DatasetFormat.JOB.value},
        files={"dataset": ("dataset.csv", valid_experiment_dataset_with_empty_gt)},
    )
    assert empty_ground_truth_response.status_code == status.HTTP_201_CREATED
    created_dataset = DatasetResponse.model_validate(empty_ground_truth_response.json())
    assert created_dataset.ground_truth is False
    location = empty_ground_truth_response.headers.get(HttpHeaders.LOCATION)
    assert location != ""
    assert location == f"{test_client.base_url}datasets/{created_dataset.id}"
