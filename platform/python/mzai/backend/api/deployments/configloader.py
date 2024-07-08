from abc import ABC, abstractmethod


class ConfigLoader(ABC):
    @abstractmethod
    def get_config_dict(self):
        pass
