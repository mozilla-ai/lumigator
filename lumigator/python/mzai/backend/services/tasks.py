from uuid import UUID

from fastapi import HTTPException, status

from mzai.backend.records.tasks import TaskRecord
from mzai.backend.repositories.tasks import TaskRepository
from mzai.schemas.extras import ListingResponse
from mzai.schemas.tasks import TaskCreate, TaskResponse


class TaskService:
    def __init__(self, tasks_repo: TaskRepository):
        self.tasks_repo = tasks_repo

    def _raise_not_found(self, task_id: UUID) -> None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Task '{task_id}' not found.")

    def _get_task_record(self, task_id: UUID) -> TaskRecord:
        record = self.tasks_repo.get(task_id)

        if record is None:
            self._raise_not_found(task_id)
        return record

    def get_task(self, task_id: UUID) -> TaskResponse:
        record = self._get_task_record(task_id)
        return TaskResponse.model_validate(record)

    def create_task(self, request: TaskCreate) -> TaskResponse:
        # Create DB record
        record = self.tasks_repo.create(
            name=request.name, description=request.description, models=request.models
        )
        return TaskResponse.model_validate(record)

    def delete_task(self, task_id: UUID) -> None:
        record = self._get_task_record(task_id)
        # Delete DB record
        self.tasks_repo.delete(record.id)

    def list_tasks(self, skip: int = 0, limit: int = 100) -> ListingResponse[TaskResponse]:
        total = self.tasks_repo.count()
        records = self.tasks_repo.list(skip, limit)
        return ListingResponse(
            total=total,
            items=[TaskResponse.model_validate(x) for x in records],
        )
