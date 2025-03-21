from uuid import UUID

from evaluator.schemas import DatasetConfig, EvalJobConfig, EvaluationConfig
from lumigator_schemas.jobs import JobCreate, JobType

from backend.services.job_interface import JobDefinition


class JobDefinitionEvaluation(JobDefinition):
    def generate_config(self, request: JobCreate, record_id: UUID, dataset_path: str, storage_path: str):
        job_config = EvalJobConfig(
            name=f"{request.name}/{record_id}",
            dataset=DatasetConfig(path=dataset_path),
            evaluation=EvaluationConfig(
                metrics=request.job_config.metrics,
                llm_as_judge=request.job_config.llm_as_judge.model_dump() if request.job_config.llm_as_judge else None,
                max_samples=request.max_samples,
                return_input_data=True,
                return_predictions=True,
                storage_path=storage_path,
            ),
        )
        return job_config

    def store_as_dataset(self) -> bool:
        return False


# Eval job details
# FIXME tweak paths in the backend
EVALUATOR_WORK_DIR = "../jobs/evaluator"
# FIXME maybe we can read the requirements file and tweak it in the backend
# otherwise, we make another method in the job interface
EVALUATOR_PIP_REQS = "../jobs/evaluator/requirements.txt"
EVALUATOR_COMMAND = str = "python evaluator.py"

JOB_DEFINITION: JobDefinition = JobDefinitionEvaluation(
    command=EVALUATOR_COMMAND,
    pip_reqs=EVALUATOR_PIP_REQS,
    work_dir=EVALUATOR_WORK_DIR,
    config_model=EvalJobConfig,
    type=JobType.EVALUATION,
)
