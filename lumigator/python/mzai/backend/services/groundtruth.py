from uuid import UUID

import loguru
import requests
from fastapi import HTTPException, status
from ray.dashboard.modules.serve.sdk import ServeSubmissionClient

from mzai.backend.api.deployments.bart_summarizer_config_loader import BartSummarizerConfigLoader
from mzai.backend.api.deployments.mistral_summarizer_config_loader import (
    MistralSummarizerConfigLoader,
)


from mzai.backend.records.groundtruth import GroundTruthDeploymentRecord
from mzai.backend.repositories.groundtruth import GroundTruthDeploymentRepository
from mzai.backend.settings import settings
from mzai.schemas.extras import ListingResponse
from mzai.schemas.groundtruth import (
    GroundTruthDeploymentCreate,
    GroundTruthDeploymentQueryResponse,
    GroundTruthDeploymentResponse,
    GroundTruthQueryRequest,
)
from mzai.backend.settings import settings
from loguru import logger
from typing import Literal


class GroundTruthService:
    def __init__(
        self,
        deployment_repo: GroundTruthDeploymentRepository,
        ray_serve_client: ServeSubmissionClient,
    ):
        self.deployment_repo = deployment_repo
        self.ray_client = ray_serve_client

    def create_deployment(self, request: GroundTruthDeploymentCreate, model_type: str):
        if model_type == "bart":
            conf = BartSummarizerConfigLoader(
                num_gpus=request.num_gpus, num_replicas=request.num_replicas
            )
        elif model_type == "mistral":
            conf = MistralSummarizerConfigLoader(
                num_gpus=request.num_gpus, num_replicas=request.num_replicas
            )
        else:
            logger.error("Model type not found, defaulting to BART")
            conf = BartSummarizerConfigLoader(
                num_gpus=request.num_gpus, num_replicas=request.num_replicas
            )

        deployment_args = conf.get_config_dict()
        deployment_name = conf.get_deployment_name()
        deployment_description = conf.get_deployment_description()

        self.ray_client.deploy_applications(deployment_args)

        record = self.deployment_repo.create(
            name=deployment_name, description=deployment_description
        )

        return GroundTruthDeploymentResponse.model_validate(record)

    def list_deployments(
        self, skip: int = 0, limit: int = 100
    ) -> (ListingResponse)[GroundTruthDeploymentResponse]:
        total = self.deployment_repo.count()
        records = self.deployment_repo.list(skip, limit)
        return ListingResponse(
            total=total,
            items=[GroundTruthDeploymentResponse.model_validate(x) for x in records],
        )

    def run_inference(self, request: GroundTruthQueryRequest) -> GroundTruthDeploymentQueryResponse:
        logger.info("Running model inference on ray ")
        try:
            base_url = f"http://{settings.RAY_HEAD_NODE_HOST}:{settings.RAY_SERVE_INFERENCE_PORT}"
            headers = {"Content-Type": "application/json"}
            response = requests.post(base_url, headers=headers, json={"text": [request.text]})
            logger.info(f"Running model inference on ray @ {base_url}, {request.text} ")
            return GroundTruthDeploymentQueryResponse(deployment_response=response.json())
        except Exception as e:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    def _get_deployment_record(self, deployment_id: UUID) -> GroundTruthDeploymentRecord:
        record = self.deployment_repo.get(deployment_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Deployment {deployment_id} not found.")
        return record

    def delete_deployment(self, deployment_id: UUID) -> None:
        self.deployment_repo.delete(deployment_id)
        return logger.info(f"{deployment_id} deleted")
