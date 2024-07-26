from typing import Any

from loguru import logger
from pydantic import BaseModel

from mzai.backend.api.deployments.configloader import ConfigLoader
from mzai.backend.settings import settings
from mzai.bart_summarizer.bart_summarizer import BARTSummarizerArgs


class RayServeActorConfig(BaseModel):
    num_cpus: float
    num_gpus: float | None = None
    num_replicas: int | None = None


class RayServeDeploymentConfig(BaseModel):
    name: str
    ray_actor_options: RayServeActorConfig


class RayServeRuntimeConfig(BaseModel):
    pip: list[str]
    working_dir: str = None


class RayAppConfig(BaseModel):
    name: str
    route_prefix: str
    import_path: str
    args: BARTSummarizerArgs
    runtime_env: RayServeRuntimeConfig
    deployments: list[RayServeDeploymentConfig]


class RayConfig(BaseModel):
    applications: list[RayAppConfig]


class BartSummarizerConfigLoader(ConfigLoader):
    def __init__(self, num_gpus: float, num_replicas: int):
        self.config = RayConfig(
            applications=[
                RayAppConfig(
                    name="bart_summarizer",
                    route_prefix="/",
                    import_path="bart_summarizer:app",
                    args=BARTSummarizerArgs(
                        name="facebook/bart-large-cnn",
                        tokenizer="facebook/bart-large-cnn",
                        task="summarization",
                        description="BART Text summarization model",
                    ),
                    runtime_env=RayServeRuntimeConfig(
                        pip=[
                            "transformers==4.38.0",
                            "torch==2.1.2",
                            "starlette==0.37.2",
                            "PyYAML==6.0.1",
                        ],
                    ),
                    deployments=[
                        RayServeDeploymentConfig(
                            name="BART Summarizer",
                            num_replicas=num_replicas,
                            ray_actor_options=RayServeActorConfig(
                                num_cpus=1.0, num_gpus=num_gpus, num_replicas=num_replicas
                            ),
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
