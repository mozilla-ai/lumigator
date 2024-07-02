from pathlib import Path
from typing import Any

import yaml
from loguru import logger
from pydantic import BaseModel

from mzai.backend.api.deployments.summarizer import SummarizerArgs


class RayServeActorConfig(BaseModel):
    num_cpus: float
    num_gpus: float


class RayServeDeploymentConfig(BaseModel):
    name: str
    num_replicas: int
    ray_actor_options: RayServeActorConfig


class RayServeRuntimeConfig(BaseModel):
    working_dir: str
    pip: list[str]


class RayAppConfig(BaseModel):
    name: str
    route_prefix: str
    import_path: str
    args: SummarizerArgs
    runtime_env: RayServeRuntimeConfig
    deployments: list[RayServeDeploymentConfig]


class RayConfig(BaseModel):
    applications: list[RayAppConfig]


class ConfigLoader:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config_model = RayConfig

    def _get_config(self):
        cwd = Path.cwd()
        config_data = yaml.safe_load(
            Path(f"{cwd}/platform/python/mzai/backend/api/{self.config_file}").read_text()
        )
        return config_data

    def get_deployment_name(self) -> str:
        config_data = self._get_config()
        model_config = self.config_model(**config_data)
        print(model_config)
        name: str = model_config.applications[0].name
        return name

    def get_deployment_description(self) -> str:
        config_data = self._get_config()
        model_config = self.config_model(**config_data)
        description: str = model_config.applications[0].args.description
        return description

    def read_config(self) -> dict[str, Any] | None:
        try:
            config_data = self._get_config()
            parsed_config = self.config_model.model_validate(config_data)
            return parsed_config.model_dump()
        except Exception as e:
            logger.info(f"Error reading configuration: {e}")
