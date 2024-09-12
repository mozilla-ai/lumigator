import contextlib
import tempfile
from pathlib import Path
from typing import Annotated, Any

import torch
from pydantic import BaseModel, BeforeValidator, PlainSerializer, WithJsonSchema
from pydantic_yaml import parse_yaml_file_as, to_yaml_file


def validate_torch_dtype(x: Any) -> torch.dtype:
    match x:
        case torch.dtype():
            return x
        case str() if hasattr(torch, x) and isinstance(getattr(torch, x), torch.dtype):
            return getattr(torch, x)
        case _:
            raise ValueError(f"{x} is not a valid torch.dtype.")


SerializableTorchDtype = Annotated[
    torch.dtype,
    BeforeValidator(lambda x: validate_torch_dtype(x)),
    PlainSerializer(lambda x: str(x).split(".")[1]),
    WithJsonSchema({"type": "string"}, mode="validation"),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]
"""Custom type validator for a `torch.dtype` object.

Accepts `torch.dtype` instances or strings representing a valid dtype from the `torch` package.
Ref: https://docs.pydantic.dev/latest/concepts/types/#custom-types
"""


class LMBuddyConfig(
    BaseModel,
    extra="forbid",
    arbitrary_types_allowed=True,
    validate_assignment=True,
):
    """Base class for all Pydantic configs in the library.

    Defines some common settings used by all subclasses.
    """

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
