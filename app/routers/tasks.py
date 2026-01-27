from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import TaskCreate, TaskUpdate
from app.services import task_service
from app.utils.response import success_response


router = APIRouter(tags=["Tasks"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create(
    task: TaskCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_task = task_service.create_task(task, user.id, db)

    return success_response(
        data=new_task,
        message="Task created successfully"
    )


@router.get("/")
def get_all(
    search: str = None,
    completed: bool = None,
    sort_by: str = "created_at",
    order: str = "desc",
    skip: int = 0,
    limit: int = 10,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    tasks = task_service.get_tasks(
        user.id,
        db,
        search,
        completed,
        sort_by,
        order,
        skip,
        limit
    )

    return success_response(
        data=tasks,
        message="Tasks retrieved successfully"
    )


@router.get("/{task_id}")
def get(
    task_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = task_service.get_task(task_id, user.id, db)

    return success_response(
        data=task,
        message="Task retrieved successfully"
    )


@router.patch("/{task_id}")
def update(
    task_id: int,
    task: TaskUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated_task = task_service.update_task(task_id, user.id, task, db)

    return success_response(
        data=updated_task,
        message="Task updated successfully"
    )


@router.delete("/{task_id}")
def delete(
    task_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task_service.delete_task(task_id, user.id, db)

    return success_response(
        message="Task deleted successfully"
    )
