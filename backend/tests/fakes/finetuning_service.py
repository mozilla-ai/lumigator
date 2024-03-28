from src.repositories.finetuning import FinetuningJobRepository
from src.schemas.finetuning import FinetuningJobCreate, FinetuningJobResponse
from src.services.finetuning import FinetuningService


class FakeFinetuningService(FinetuningService):
    """Fake finetuning service that elides interactions with Ray."""

    def __init__(self, job_repo: FinetuningJobRepository):
        super().__init__(job_repo, ray_client=None)

    def create_job(self, request: FinetuningJobCreate) -> FinetuningJobResponse:
        return self.job_repo.create(
            name=request.name,
            description=request.description,
            submission_id="",
        )
