from uuid import UUID

from evaluator.schemas import DatasetConfig, EvalJobConfig, EvaluationConfig
from lumigator_schemas.jobs import JobCreate

from backend.services.job_interface import JobInterface


class JobInterfaceEvalLite(JobInterface):
    def generate_config(self, request: JobCreate, record_id: UUID, dataset_path: str, storage_path: str):
        job_config = EvalJobConfig(
            name=f"{request.name}/{record_id}",
            dataset=DatasetConfig(path=dataset_path),
            evaluation=EvaluationConfig(
                metrics=request.job_config.metrics,
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
EVALUATOR_WORK_DIR = "../jobs/evaluate"
# FIXME maybe we can read the requirements file and tweak it in the backend
# otherwise, we make another method in the job interface
EVALUATOR_PIP_REQS = "requirements_cpu.txt"
EVALUATOR_COMMAND = str = "python evaluator.py"

JOB_INTERFACE = JobInterfaceEvalLite(
    command=EVALUATOR_COMMAND,
    pip_reqs=EVALUATOR_PIP_REQS,
    work_dir=EVALUATOR_WORK_DIR,
    config_model=EvalJobConfig,
)
