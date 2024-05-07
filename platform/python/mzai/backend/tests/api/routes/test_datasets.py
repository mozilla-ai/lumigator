import csv
import io

import pytest

from mzai.schemas.datasets import DatasetFormat


@pytest.fixture
def experiment_dataset() -> io.BytesIO:
    str_obj = io.StringIO()
    data = [["input", "target"], ["Hello World", "Hello"]]
    csv.writer(str_obj).writerows(data)
    return io.BytesIO(str_obj.read().encode("utf-8"))


def test_dataset_upload(app_client, experiment_dataset):
    response = app_client.post(
        url="/datasets",
        data={"format": DatasetFormat.EXPERIMENT.value},
        files={"dataset": ("dataset.csv", experiment_dataset, "multipart/form-data")},
    )
    raise ValueError(f"{response}")
