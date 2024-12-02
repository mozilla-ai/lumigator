from s3fs import S3FileSystem

from backend.repositories.datasets import DatasetRepository
from backend.services.datasets import DatasetService


def test_delete_dataset_file_not_found(db_session, fake_s3_client, fake_s3fs):
    filename = "dataset.csv"
    format = "job"
    dataset_repo = DatasetRepository(db_session)
    dataset_record = dataset_repo.create(
        filename=filename, format=format, size=123, ground_truth=True
    )
    assert dataset_record is not None
    assert dataset_record.filename == filename
    assert dataset_record.format == format
    dataset_service = DatasetService(dataset_repo, fake_s3_client, fake_s3fs)
    dataset_service.delete_dataset(dataset_record.id)
    dataset_record = dataset_service._get_dataset_record(dataset_record.id)
    assert dataset_record is None
