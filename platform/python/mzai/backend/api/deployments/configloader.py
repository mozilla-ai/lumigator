import yaml
from typing import List, Any
from pydantic import BaseModel
from pathlib import Path
from mzai.backend.api.deployments.summarizer import SummarizerArgs


class RayServeActorConfig(BaseModel):
    num_cpus: float
    num_gpus: float


class RayArgs(BaseModel):
    model: str
    tokenizer: str
    task: str


class RayServeDeploymentConfig(BaseModel):
    name: str
    num_replicas: int
    ray_actor_options: RayServeActorConfig


class RayServeRuntimeConfig(BaseModel):
    working_dir: str
    pip: List[str]


class RayAppConfig(BaseModel):
    name: str
    route_prefix: str
    import_path: str
    args: SummarizerArgs
    runtime_env: RayServeRuntimeConfig
    deployments: List[RayServeDeploymentConfig]


class RayConfig(BaseModel):
    applications: List[RayAppConfig]


class ConfigLoader:
    def __init__(self, config_file: str) -> dict:
        self.config_file = config_file
        self.config_model = RayConfig

    def read_config(self) -> Any:
        try:
            cwd = Path.cwd()
            config_data = yaml.safe_load(Path(f'{cwd}/{self.config_file}').read_text())
            parsed_config = self.config_model.model_validate(config_data)
            return parsed_config.dict()
        except Exception as e:
            print(f"Error reading configuration: {e}")
            return None
