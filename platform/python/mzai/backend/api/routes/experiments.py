from uuid import UUID

from fastapi import APIRouter

router = APIRouter()


@router.post("/")
def create_experiment():
    pass


@router.get("/{experiment_id}")
def get_experiment(experiment_id: UUID):
    pass


@router.get("/")
def list_experiments(skip: int = 0, limit: int = 100):
    pass


@router.get("/{experiment_id}/result")
def get_experiment_result(experiment_id: UUID):
    pass
