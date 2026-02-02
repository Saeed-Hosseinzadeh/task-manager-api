from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from fastapi import HTTPException, status

from app.models import Task
from app.schemas import TaskCreate, TaskUpdate


def create_task(task_data: TaskCreate, user_id: int, db: Session) -> Task:
    """
    Create a new task for a specific user.
    """

    task = Task(
        title=task_data.title,
        description=task_data.description,
        is_completed=task_data.is_completed,
        owner_id=user_id
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def get_tasks(
    user_id: int,
    db: Session,
    search: str | None = None,
    completed: bool | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
    skip: int = 0,
    limit: int = 10
) -> dict:
    """
    Retrieve tasks belonging to a specific user with filtering,
    searching, sorting, and pagination.
    """

    query = db.query(Task).filter(Task.owner_id == user_id)

    # Search by title (case-insensitive)
    if search:
        query = query.filter(Task.title.ilike(f"%{search}%"))

    # Filter by completion status
    if completed is not None:
        query = query.filter(Task.is_completed == completed)

    # Validate sort column
    allowed_sort_fields = {"created_at", "title", "is_completed"}
    if sort_by not in allowed_sort_fields:
        sort_by = "created_at"

    sort_column = getattr(Task, sort_by)

    if order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    total = query.count()

    tasks = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "tasks": tasks
    }


def get_task(task_id: int, user_id: int, db: Session) -> Task:
    """
    Retrieve a single task belonging to the specified user.
    """

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == user_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


def update_task(task_id: int, user_id: int, task_data: TaskUpdate, db: Session) -> Task:
    """
    Update an existing task.
    Only provided fields will be updated.
    """

    task = get_task(task_id, user_id, db)

    update_data = task_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


def delete_task(task_id: int, user_id: int, db: Session) -> None:
    """
    Delete a task belonging to the user.
    """

    task = get_task(task_id, user_id, db)

    db.delete(task)
    db.commit()
