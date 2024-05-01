from uuid import UUID

from fastapi import UploadFile

from mzai.backend.repositories.datasets import DatasetRepository
from mzai.schemas.datasets import DatasetFormat, DatasetResponse
from mzai.schemas.extras import ListingResponse


class DatasetService:
    DATASET_BUCKET_PREFIX: str = "datasets"

    def __init__(self, dataset_repo: DatasetRepository, s3_client):
        self.dataset_repo = dataset_repo
        self.s3_client = s3_client

    def upload_dataset(self, dataset: UploadFile, format: DatasetFormat) -> DatasetResponse:
        pass

    def get_dataset(self, dataset_id: UUID) -> DatasetResponse:
        pass

    def get_dataset_download(self, dataset_id: UUID) -> DatasetResponse:
        pass

    def list_datasets(self, skip: int = 0, limit: int = 100) -> ListingResponse[DatasetResponse]:
        pass
