from typing import Any

from loguru import logger
from pydantic import BaseModel
from uuid import UUID

from mzai.backend.api.deployments.configloader import ConfigLoader
from mzai.backend.settings import settings
from mzai.summarizer.summarizer import SummarizerArgs


class RayServeActorConfig(BaseModel):
    num_cpus: float | None = None
    num_gpus: float | None = None


class RayServeDeploymentConfig(BaseModel):
    name: str
    num_replicas: int | None = None
    ray_actor_options: RayServeActorConfig


class RayServeRuntimeConfig(BaseModel):
    pip: list[str]
    working_dir: str = None
    env_vars: dict[str, str]


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
    def __init__(self, num_gpus: float, num_replicas: int):
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
                        description="",
                    ),
                    runtime_env=RayServeRuntimeConfig(
                        pip=[
                            "transformers==4.38.0",
                            "torch==2.1.2",
                            "starlette==0.37.2",
                            "PyYAML==6.0.1",
                        ],
                        env_vars={"CUDA_LAUNCH_BLOCKING": "1"},
                    ),
                    deployments=[
                        RayServeDeploymentConfig(
                            name="Summarizer",
                            num_replicas=num_replicas,
                            ray_actor_options=RayServeActorConfig(num_cpus=1.0, num_gpus=num_gpus),
                        )
                    ],
                )
            ]
        )
        if settings.SUMMARIZER_WORK_DIR is not None:
            self.config.applications[0].runtime_env.working_dir = settings.SUMMARIZER_WORK_DIR

    def get_deployment_name(self) -> str:
        config = self.config
        name: str = config.applications[0].name
        return name

    def set_deployment_description(self, uuid: UUID):
        """set the description to the Lumigator UUID."""
        self.config.applications[0].args.description = str(uuid)

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
