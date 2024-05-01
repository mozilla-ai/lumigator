from fastapi import UploadFile

from mzai.schemas.datasets import DatasetFormat, DatasetResponse


class DatasetService:
    DATASET_BUCKET_PREFIX: str = "datasets"

    def __init__(self, s3_client):
        self.s3_client = s3_client

    def upload_dataset(self, dataset: UploadFile, format: DatasetFormat) -> DatasetResponse:
        pass
