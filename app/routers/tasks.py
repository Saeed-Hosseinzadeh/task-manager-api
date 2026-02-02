from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.services import task_service
from app.utils.response import success_response
from app.models import User


router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task for the authenticated user.
    """
    new_task = task_service.create_task(task, user.id, db)

    return success_response(
        data=new_task,
        message="Task created successfully"
    )


@router.get("/")
def get_tasks(
    search: str | None = Query(None, description="Search tasks by title"),
    completed: bool | None = Query(None, description="Filter by completion status"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    order: str = Query("desc", description="Sort order: asc or desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a paginated list of tasks for the authenticated user.
    Supports searching, filtering, sorting, and pagination.
    """

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
def get_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific task by its ID.
    """

    task = task_service.get_task(task_id, user.id, db)

    return success_response(
        data=task,
        message="Task retrieved successfully"
    )


@router.patch("/{task_id}")
def update_task(
    task_id: int,
    task: TaskUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing task belonging to the authenticated user.
    """

    updated_task = task_service.update_task(task_id, user.id, task, db)

    return success_response(
        data=updated_task,
        message="Task updated successfully"
    )


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a task belonging to the authenticated user.
    """

    task_service.delete_task(task_id, user.id, db)

    return success_response(
        message="Task deleted successfully"
    )
