from abc import ABC, abstractmethod
from typing import Any


class RayJobEntrypoint(ABC):
    @property
    @abstractmethod
    def command(self) -> str:
        pass

    @property
    def runtime_env(self) -> dict[str, Any] | None:
        return None

    @property
    def num_cpus(self) -> int | float | None:
        return None

    @property
    def num_gpus(self) -> int | float | None:
        return None

    @property
    def memory(self) -> int | float | None:
        return None


class FinetuningJobEntrypoint(RayJobEntrypoint):
    pass
