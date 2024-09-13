from uuid import UUID

from fastapi import APIRouter, status

from mzai.backend.api.deps import TaskServiceDep
from mzai.schemas.extras import ListingResponse
from mzai.schemas.tasks import TaskCreate, TaskResponse

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_task(service: TaskServiceDep, request: TaskCreate) -> TaskResponse:
    return service.create_task(request)


@router.get("/{task_id}")
def get_task(service: TaskServiceDep, task_id: UUID) -> TaskResponse:
    return service.get_task(task_id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(service: TaskServiceDep, task_id: UUID) -> None:
    service.delete_task(task_id)


@router.get("/")
def list_tasks(
    service: TaskServiceDep,
    skip: int = 0,
    limit: int = 100,
) -> ListingResponse[TaskResponse]:
    return service.list_tasks(skip, limit)
