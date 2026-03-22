"""
Tasks Router

This module defines task-related API endpoints.

Endpoints included:
- Create a new task
- Retrieve a list of tasks
- Retrieve a specific task
- Update an existing task
- Delete a task

Important
---------
The '/tasks' prefix is NOT defined in this router.

The prefix is applied in the main application when this router
is included using:

    app.include_router(tasks.router, prefix="/tasks")

This prevents route duplication such as:

    /tasks/tasks/

Expected final routes:
- POST /tasks/
- GET /tasks/
- GET /tasks/{task_id}
- PATCH /tasks/{task_id}
- DELETE /tasks/{task_id}
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

# Import database dependency
from app.database import get_db

# Import authentication dependency
from app.dependencies import get_current_user

# Import request and response schemas
from app.schemas import TaskCreate, TaskUpdate, TaskResponse

# Import task service layer
from app.services import task_service

# Import standard API response helper
from app.utils.response import success_response

# Import User model for typing the authenticated user
from app.models import User


# Create tasks router.
# Do NOT add prefix="/tasks" here.
# The /tasks prefix is added in app/main.py.
router = APIRouter(tags=["Tasks"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new task for the authenticated user.

    This endpoint receives task creation data, gets the currently
    authenticated user, and delegates task creation to the service layer.

    Parameters
    ----------
    task : TaskCreate
        Payload containing task creation data.

    user : User
        Currently authenticated user injected by the authentication
        dependency.

    db : Session
        SQLAlchemy database session injected by FastAPI dependency system.

    Returns
    -------
    dict
        Standard success response containing the created task.

    Raises
    ------
    HTTPException
        Raised by dependencies or the service layer if authentication
        fails or task creation is invalid.
    """

    # Delegate task creation business logic to the service layer.
    new_task = task_service.create_task(task, user.id, db)

    return success_response(
        data=new_task,
        message="Task created successfully",
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
    db: Session = Depends(get_db),
):
    """
    Retrieve a paginated list of tasks for the authenticated user.

    This endpoint supports searching, filtering, sorting, and pagination.
    Only tasks belonging to the currently authenticated user are returned.

    Parameters
    ----------
    search : str | None
        Optional search keyword used to filter tasks by title.

    completed : bool | None
        Optional completion status filter.

    sort_by : str
        Field name used for sorting results.

    order : str
        Sort order. Expected values are typically 'asc' or 'desc'.

    skip : int
        Number of records to skip for pagination.

    limit : int
        Maximum number of records to return.

    user : User
        Currently authenticated user injected by the authentication
        dependency.

    db : Session
        SQLAlchemy database session injected by FastAPI dependency system.

    Returns
    -------
    dict
        Standard success response containing the user's task list.

    Raises
    ------
    HTTPException
        Raised by dependencies or the service layer if authentication
        fails or query parameters are invalid.
    """

    # Delegate task retrieval logic to the service layer.
    tasks = task_service.get_tasks(
        user.id,
        db,
        search,
        completed,
        sort_by,
        order,
        skip,
        limit,
    )

    return success_response(
        data=tasks,
        message="Tasks retrieved successfully",
    )


@router.get("/{task_id}")
def get_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific task by its ID.

    This endpoint returns a single task only if it belongs to the
    currently authenticated user.

    Parameters
    ----------
    task_id : int
        ID of the task to retrieve.

    user : User
        Currently authenticated user injected by the authentication
        dependency.

    db : Session
        SQLAlchemy database session injected by FastAPI dependency system.

    Returns
    -------
    dict
        Standard success response containing the requested task.

    Raises
    ------
    HTTPException
        Raised by dependencies or the service layer if authentication
        fails, the task does not exist, or the task does not belong to
        the current user.
    """

    # Delegate single-task retrieval logic to the service layer.
    task = task_service.get_task(task_id, user.id, db)

    return success_response(
        data=task,
        message="Task retrieved successfully",
    )


@router.patch("/{task_id}")
def update_task(
    task_id: int,
    task: TaskUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing task belonging to the authenticated user.

    This endpoint receives task update data and updates the task only
    if it belongs to the currently authenticated user.

    Parameters
    ----------
    task_id : int
        ID of the task to update.

    task : TaskUpdate
        Payload containing fields that should be updated.

    user : User
        Currently authenticated user injected by the authentication
        dependency.

    db : Session
        SQLAlchemy database session injected by FastAPI dependency system.

    Returns
    -------
    dict
        Standard success response containing the updated task.

    Raises
    ------
    HTTPException
        Raised by dependencies or the service layer if authentication
        fails, the task does not exist, or the task does not belong to
        the current user.
    """

    # Delegate task update logic to the service layer.
    updated_task = task_service.update_task(task_id, user.id, task, db)

    return success_response(
        data=updated_task,
        message="Task updated successfully",
    )


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a task belonging to the authenticated user.

    This endpoint deletes a task only if it belongs to the currently
    authenticated user.

    Parameters
    ----------
    task_id : int
        ID of the task to delete.

    user : User
        Currently authenticated user injected by the authentication
        dependency.

    db : Session
        SQLAlchemy database session injected by FastAPI dependency system.

    Returns
    -------
    dict
        Standard success response confirming task deletion.

    Raises
    ------
    HTTPException
        Raised by dependencies or the service layer if authentication
        fails, the task does not exist, or the task does not belong to
        the current user.
    """

    # Delegate task deletion logic to the service layer.
    task_service.delete_task(task_id, user.id, db)

    return success_response(
        message="Task deleted successfully",
    )
