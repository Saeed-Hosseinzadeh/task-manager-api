"""
Task Service Layer

This module implements the core business logic for task management.
It provides an abstraction layer between the API routes and the
database models, ensuring that task operations respect user
ownership and support filtering, sorting, and pagination.

Responsibilities
----------------
- Task creation
- Task retrieval (single and multiple)
- Task updates
- Task deletion
- Filtering, searching, sorting, and pagination

Design Notes
------------
All task operations are restricted to the owning user to ensure
data isolation and security. The service layer centralizes these
rules so that API routes remain lightweight and focused only on
request/response handling.
"""

from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from fastapi import HTTPException, status

from app.models import Task
from app.schemas import TaskCreate, TaskUpdate


def create_task(task_data: TaskCreate, user_id: int, db: Session) -> Task:
    """
    Create a new task for a specific user.

    The task is created using validated input data and associated
    with the provided user identifier.

    Args:
        task_data (TaskCreate):
            Validated task payload containing title, description,
            and completion status.

        user_id (int):
            Identifier of the user who owns the task.

        db (Session):
            Active SQLAlchemy database session.

    Returns:
        Task:
            The newly created Task ORM instance persisted in the database.
    """

    # Create a new task associated with the given user.
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
    Retrieve tasks belonging to a specific user.

    This function supports optional filtering, case-insensitive
    search by title, configurable sorting, and pagination.

    Args:
        user_id (int):
            Identifier of the task owner.

        db (Session):
            Active SQLAlchemy database session.

        search (str | None, optional):
            Case-insensitive search string applied to the task title.

        completed (bool | None, optional):
            Filter tasks by completion status.

        sort_by (str):
            Field used for sorting results.
            Allowed values: "created_at", "title", "is_completed".

        order (str):
            Sort direction ("asc" or "desc").

        skip (int):
            Number of records to skip for pagination.

        limit (int):
            Maximum number of tasks returned in the result.

    Returns:
        dict:
            Dictionary containing query results:

            - total (int): Total number of tasks matching the filters.
            - tasks (list[Task]): List of task ORM objects.
    """

    # Base query restricted to tasks owned by the specified user.
    query = db.query(Task).filter(Task.owner_id == user_id)

    # Apply case-insensitive title search if provided.
    if search:
        query = query.filter(Task.title.ilike(f"%{search}%"))

    # Apply completion status filter if specified.
    if completed is not None:
        query = query.filter(Task.is_completed == completed)

    # Validate sorting field to prevent invalid attribute access.
    allowed_sort_fields = {"created_at", "title", "is_completed"}
    if sort_by not in allowed_sort_fields:
        sort_by = "created_at"

    sort_column = getattr(Task, sort_by)

    # Apply sorting direction.
    if order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # Calculate total number of matching records before pagination.
    total = query.count()

    # Apply pagination.
    tasks = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "tasks": tasks
    }


def get_task(task_id: int, user_id: int, db: Session) -> Task:
    """
    Retrieve a single task owned by a specific user.

    The query ensures that the requested task belongs to the
    provided user identifier.

    Args:
        task_id (int):
            Unique identifier of the task.

        user_id (int):
            Identifier of the user who owns the task.

        db (Session):
            Active SQLAlchemy database session.

    Returns:
        Task:
            The matching task ORM instance.

    Raises:
        HTTPException:
            Raised if the task does not exist or does not belong
            to the specified user.
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

    Only the fields explicitly provided in the request payload
    will be updated. The task must belong to the specified user.

    Args:
        task_id (int):
            Identifier of the task to update.

        user_id (int):
            Identifier of the task owner.

        task_data (TaskUpdate):
            Validated update payload.

        db (Session):
            Active SQLAlchemy database session.

    Returns:
        Task:
            The updated task ORM instance.
    """

    # Retrieve the task and validate ownership.
    task = get_task(task_id, user_id, db)

    # Extract only the fields explicitly provided in the update payload.
    update_data = task_data.model_dump(exclude_unset=True)

    # Dynamically update model attributes.
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


def delete_task(task_id: int, user_id: int, db: Session) -> None:
    """
    Delete a task owned by a specific user.

    The task must belong to the provided user identifier before
    it can be removed from the database.

    Args:
        task_id (int):
            Identifier of the task to delete.

        user_id (int):
            Identifier of the task owner.

        db (Session):
            Active SQLAlchemy database session.
    """

    # Retrieve the task and ensure it belongs to the user.
    task = get_task(task_id, user_id, db)

    db.delete(task)
    db.commit()
