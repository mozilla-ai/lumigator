from enum import Enum
from pathlib import Path
from urllib.parse import ParseResult, urlparse

import pandas as pd
import wandb

from lm_buddy.paths import PathPrefix


class ArtifactType(str, Enum):
    """Enumeration of artifact types used by the LM Buddy."""

    DATASET = "dataset"
    MODEL = "model"
    TOKENIZER = "tokenizer"
    EVALUATION = "evaluation"


def default_artifact_name(job_name: str, artifact_type: ArtifactType) -> str:
    """A default name for an artifact based on the job name and type."""
    return f"{job_name}-{artifact_type}"


def get_artifact_from_api(artifact_name: str) -> wandb.Artifact:
    """Retrieve an artifact by fully qualified name from the W&B API.

    This does not handle linking the artifact to an active run.
    For that, use `run.use_artifact(artifact_name)`.
    """
    api = wandb.Api()
    return api.artifact(artifact_name)


def get_artifact_directory(
    artifact: wandb.Artifact, *, download_root_path: str | None = None
) -> Path:
    """Get the directory containing the artifact's data.

    If the artifact references data already on the filesystem, simply return that path.
    If not, downloads the artifact (with the specified `download_root_path`)
    and returns the newly created artifact directory path.
    """
    for entry in artifact.manifest.entries.values():
        match urlparse(entry.ref):
            case ParseResult(scheme="file", path=file_path):
                return Path(file_path).parent
    # No filesystem references found in the manifest -> download the artifact
    download_path = artifact.download(root=download_root_path)
    return Path(download_path)


def build_directory_artifact(
    artifact_name: str,
    artifact_type: ArtifactType,
    dir_path: str | Path,
    *,
    reference: bool = False,
    entry_name: str | None = None,
    max_objects: int | None = None,
) -> wandb.Artifact:
    """Build an artifact containing the contents of a directory.

    Args:
        artifact_name (str): Name of the artifact.
        artifact_type (ArtifactType): Type of artifact.
        dir_path (str | Path): Directory path to include in the artifact.

    Keyword Args:
        reference (bool): Only reference the directory, do not copy contents. Defaults to False.
        entry_name (str | None): Name for directory within the artifact. Defaults to None.
        max_objects (int | None): Max objects to include in the artifact. Defaults to None.

    Returns:
        wandb.Artifact: The generated artifact.
    """
    artifact = wandb.Artifact(name=artifact_name, type=artifact_type)
    if reference:
        # Right now, we are assuming a fixed "file" URI scheme
        # We can pass the URI scheme if necessary later
        artifact.add_reference(
            uri=f"{PathPrefix.FILE.value}{dir_path}",
            max_objects=max_objects,
            name=entry_name,
        )
    else:
        artifact.add_dir(str(dir_path), name=entry_name)
    return artifact


def build_table_artifact(
    artifact_name: str,
    artifact_type: ArtifactType,
    tables: dict[str, pd.DataFrame],
) -> wandb.Artifact:
    """Build an artifact containing one or more table entries.

    Args:
        artifact_name (str): Name of the artifact.
        artifact_type (ArtifactType): Type of artifact.
        tables (dict[str, pd.DataFrame]): Mapping from table name to table data
            in the form of a `pd.DataFrame` object.

    Returns:
        wandb.Artifact: The artifact containing the table(s).
    """
    artifact = wandb.Artifact(artifact_name, type=artifact_type)
    for table_name, table_data in tables.items():
        table = wandb.Table(data=table_data)
        artifact.add(table, name=table_name)
    return artifact
