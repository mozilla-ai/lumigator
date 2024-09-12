"""
This file is used to provide fixtures for the test session accessible to all LM Buddy submodules.
"""
from pathlib import Path

import pytest

from lm_buddy.tracking.artifact_utils import ArtifactType, build_directory_artifact


@pytest.fixture(scope="session")
def examples_dir():
    return Path(__file__).parents[1] / "examples"


@pytest.fixture(scope="session")
def resources_dir():
    return Path(__file__).parent / "resources"


@pytest.fixture
def xyz_dataset_path(resources_dir):
    return resources_dir / "datasets" / "xyz"


@pytest.fixture
def text_dataset_path(resources_dir):
    return resources_dir / "datasets" / "tiny_shakespeare"


@pytest.fixture
def llm_model_path(resources_dir):
    return resources_dir / "models" / "tiny_gpt2"


@pytest.fixture
def xyz_dataset_artifact(xyz_dataset_path):
    return build_directory_artifact(
        artifact_name="xyz-dataset",
        artifact_type=ArtifactType.DATASET,
        dir_path=xyz_dataset_path,
        reference=True,
    )


@pytest.fixture
def text_dataset_artifact(text_dataset_path):
    return build_directory_artifact(
        artifact_name="tiny-shakespeare-dataset",
        artifact_type=ArtifactType.DATASET,
        dir_path=text_dataset_path,
        reference=True,
    )


@pytest.fixture
def llm_model_artifact(llm_model_path):
    return build_directory_artifact(
        artifact_name="tiny-gpt2-model",
        artifact_type=ArtifactType.MODEL,
        dir_path=llm_model_path,
        reference=True,
    )
