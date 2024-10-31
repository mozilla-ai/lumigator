import csv
import io
import uuid
from unittest.mock import Mock, patch
from urllib.parse import urlparse
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from schemas.datasets import DatasetDownloadResponse, DatasetFormat, DatasetResponse

def test_dataset_delete_error(app_client: TestClient):
    dataset_id = uuid.uuid4()
    with patch(
            "backend.services.datasets.DatasetService.delete_dataset",
            side_effect=Exception("argh I am exceptional")):
        resp = app_client.delete(f"/datasets/{dataset_id}")
        assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = resp.json()
        assert data["detail"] == f"Unexpected error deleting dataset for ID: {dataset_id}"
