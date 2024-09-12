import contextlib
import tempfile
from abc import abstractmethod
from pathlib import Path

from pydantic import Field
from pydantic_yaml import parse_yaml_file_as, to_yaml_file

from lm_buddy.configs.common import LMBuddyConfig
from lm_buddy.configs.wandb import WandbRunConfig
from lm_buddy.paths import AssetPath, PathPrefix


class JobConfig(LMBuddyConfig):
    """Configuration that comprises the entire input to an LM Buddy job.

    This class implements helper methods for de/serializing the configuration from file.

    Currently, there is a 1:1 mapping between job entrypoints and job config implementations,
    but this is not rigidly constrained by the interface. This may change in the future.
    """

    name: str = Field(description="Name of the job.")
    tracking: WandbRunConfig | None = Field(
        default=None,
        description=(
            "Tracking information to associate with the job. "
            "A new run is created with these details."
        ),
    )

    @classmethod
    def from_yaml_file(cls, path: Path | str):
        return parse_yaml_file_as(cls, path)

    def to_yaml_file(self, path: Path | str):
        to_yaml_file(path, self, exclude_none=True)

    @contextlib.contextmanager
    def to_tempfile(self, *, name: str = "config.yaml", dir: str | Path | None = None):
        """Enter a context manager with the config written to a temporary YAML file.

        Keyword Args:
            name (str): Name of the config file in the tmp directory. Defaults to "config.yaml".
            dir (str | Path | None): Root path of the temporary directory. Defaults to None.

        Returns:
            Path to the temporary config file.
        """
        with tempfile.TemporaryDirectory(dir=dir) as tmpdir:
            config_path = Path(tmpdir) / name
            self.to_yaml_file(config_path)
            yield config_path

    @abstractmethod
    def asset_paths(self) -> set[AssetPath]:
        """Return a set of all `AssetPath` fields on this config."""
        pass

    def artifact_paths(self) -> set[AssetPath]:
        """Return a set of all W&B artifact paths on this config."""
        return {x for x in self.asset_paths() if x.startswith(PathPrefix.WANDB)}
