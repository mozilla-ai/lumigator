from uuid import UUID

from fastapi import HTTPException, status
from ray.job_submission import JobSubmissionClient

from mzai.backend.jobs.submission import RayJobEntrypoint, submit_ray_job
from mzai.backend.records.experiments import ExperimentRecord
from mzai.backend.repositories.experiments import ExperimentRepository, ExperimentResultRepository
from mzai.schemas.experiments import ExperimentCreate, ExperimentResponse, ExperimentResultResponse
from mzai.schemas.extras import ListingResponse
from mzai.schemas.jobs import JobConfig, JobType


class ExperimentService:
    def __init__(
        self,
        experiment_repo: ExperimentRepository,
        result_repo: ExperimentResultRepository,
        ray_client: JobSubmissionClient,
    ):
        self.experiment_repo = experiment_repo
        self.result_repo = result_repo
        self.ray_client = ray_client

    def _get_experiment_record(self, experiment_id: UUID) -> ExperimentRecord:
        record = self.experiment_repo.get(experiment_id)
        if record is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"Experiment '{experiment_id}' not found.",
            )
        return record

    def create_experiment(self, request: ExperimentCreate) -> ExperimentResponse:
        record = self.experiment_repo.create(name=request.name, description=request.description)

        # Submit the job to Ray
        config = JobConfig(id=record.id, type=JobType.EXPERIMENT, args={"name": request.name})
        entrypoint = RayJobEntrypoint(config=config)
        submit_ray_job(self.ray_client, entrypoint)

        return ExperimentResponse.model_validate(record)

    def get_experiment(self, experiment_id: UUID) -> ExperimentResponse:
        record = self._get_experiment_record(experiment_id)
        return ExperimentResponse.model_validate(record)

    def list_experiments(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> ListingResponse[ExperimentResponse]:
        total = self.experiment_repo.count()
        records = self.experiment_repo.list(skip, limit)
        return ListingResponse(
            total=total,
            items=[ExperimentResponse.model_validate(x) for x in records],
        )

    def get_experiment_result(self, experiment_id: UUID) -> ExperimentResultResponse:
        experiment_record = self._get_experiment_record(experiment_id)
        result_record = self.result_repo.get_by_experiment_id(experiment_id)
        if result_record is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                (
                    f"No result available for experiment '{experiment_record.name}' "
                    f"(status = '{experiment_record.status}')."
                ),
            )
        return ExperimentResultResponse.model_validate(result_record)
