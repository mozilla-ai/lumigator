from typing import Any

from loguru import logger
from pydantic import BaseModel

from mzai.backend.api.deployments.configloader import ConfigLoader
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


class SummarizerConfigLoader(ConfigLoader):
    def __init__(self):
        self.config = RayConfig(
            applications=[
                RayAppConfig(
                    name="summarizer",
                    route_prefix="/",
                    import_path="summarizer:app",
                    args=SummarizerArgs(
                        name="facebook/bart-large-cnn",
                        tokenizer="facebook/bart-large-cnn",
                        task="summarization",
                        description="Text summarization model",
                    ),
                    runtime_env=RayServeRuntimeConfig(
                        working_dir="https://github.com/mozilla-ai/lm-serve/archive/df938d36573bf0e333154c0d84f4270df6785dd0.zip",
                        pip=[
                            "transformers==4.38.0",
                            "torch==2.1.2",
                            "starlette==0.37.2",
                            "PyYAML==6.0.1",
                        ],
                    ),
                    deployments=[
                        RayServeDeploymentConfig(
                            name="Summarizer",
                            num_replicas=1,
                            ray_actor_options=RayServeActorConfig(num_cpus=1.0, num_gpus=1.0),
                        )
                    ],
                )
            ]
        )

    def get_deployment_name(self) -> str:
        config = self.config
        name: str = config.applications[0].name
        return name

    def get_deployment_description(self) -> str:
        config = self.config
        description: str = config.applications[0].args.description
        return description

    def get_config_dict(self) -> dict[str, Any] | None:
        try:
            config = self.config
            return config.model_dump()
        except Exception as e:
            logger.info(f"Error reading configuration: {e}")
