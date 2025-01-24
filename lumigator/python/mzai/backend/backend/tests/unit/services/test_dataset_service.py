from uuid import UUID

import pytest
from lumigator_schemas.datasets import DatasetFormat

from backend.repositories.datasets import DatasetRepository
from backend.services.datasets import DatasetService, dataset_has_gt


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


def test_upload_dataset(db_session, fake_s3_client, fake_s3fs, valid_upload_file):
    dataset_service = DatasetService(DatasetRepository(db_session), fake_s3_client, fake_s3fs)
    upload_response = dataset_service.upload_dataset(valid_upload_file, DatasetFormat.JOB)

    assert upload_response.id is not None
    assert isinstance(upload_response.id, UUID)


@pytest.mark.parametrize(
    "extension, total",
    [
        ("foo", 0),
        ("csv", 1),
        ("  csv ", 1),
        ("CSV", 1),
        ("cSv", 1),
        ("json", 2),
        ("", 4),
        ("    ", 4),
    ],
)
def test_dataset_download_with_extensions(
    db_session, fake_s3_client, fake_s3fs, valid_upload_file, extension, total
):
    dataset_service = DatasetService(DatasetRepository(db_session), fake_s3_client, fake_s3fs)
    upload_response = dataset_service.upload_dataset(valid_upload_file, DatasetFormat.JOB)

    assert upload_response.id is not None
    assert isinstance(upload_response.id, UUID)

    download_response = dataset_service.get_dataset_download(upload_response.id, extension)
    assert download_response.id is not None
    assert isinstance(download_response.id, UUID)
    # 4 files total (HF dataset: 1 x arrow file + 2 x json) + 1 CSV.
    assert len(download_response.download_urls) == total
    assert (
        sum(1 for x in download_response.download_urls if x.endswith(extension.strip().lower()))
        == total
    )


@pytest.mark.parametrize(
    "dataset_filename, expected_ground_truth",
    [
        ("dialogsum_exc.csv", True),
        ("dialogsum_mini_empty_gt.csv", False),
        ("dialogsum_mini_no_gt.csv", False),
        ("dialogsum_mini_some_missing_some_whitespace_gt.csv", False),
        ("dialogsum_mini_all_gt_is_whitespace.csv", False),
    ],
)
def test_dataset_has_ground_truth(
    common_resources_sample_data_dir, dataset_filename, expected_ground_truth
):
    filename = str(common_resources_sample_data_dir / dataset_filename)
    has_gt = dataset_has_gt(filename)
    assert has_gt == expected_ground_truth
