"""
Tasks Router

This module defines the HTTP API endpoints responsible for task
management operations.

Responsibilities
----------------
- Task creation
- Task retrieval (single and multiple)
- Task update
- Task deletion

Architecture
------------
This router acts as the API layer and delegates all business logic
to the task service layer. It remains intentionally lightweight and
focuses only on:

- Request validation
- Dependency injection
- Delegation to services
- Response formatting

Router Prefix
-------------
The '/tasks' prefix is intentionally NOT defined inside this router.

The prefix must be applied when including the router in the FastAPI
application instance:

    app.include_router(tasks.router, prefix="/tasks")

This prevents duplicate routes such as:

    /tasks/tasks/

Expected Final Endpoints
------------------------
POST    /tasks/
GET     /tasks/
GET     /tasks/{task_id}
PATCH   /tasks/{task_id}
DELETE  /tasks/{task_id}
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

# Database dependency used to provide a SQLAlchemy session.
from app.database import get_db

# Authentication dependency that injects the current authenticated user.
from app.dependencies import get_current_user

# Request and response schemas used for validation and serialization.
from app.schemas import TaskCreate, TaskUpdate, TaskResponse

# Service layer responsible for task business logic.
from app.services import task_service

# Utility for creating standardized API responses.
from app.utils.response import success_response

# User model used for typing the authenticated user dependency.
from app.models import User


# Router instance for task-related endpoints.
# The '/tasks' prefix is applied in the main application file.
router = APIRouter(tags=["Tasks"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new task for the authenticated user.

    The task is created using validated request data and associated
    with the currently authenticated user. Authentication and database
    session management are handled through FastAPI dependency injection.

    Parameters
    ----------
    task : TaskCreate
        Validated request payload containing task creation data.

    user : User
        The authenticated user resolved by the authentication dependency.

    db : Session
        SQLAlchemy database session provided by the dependency system.

    Returns
    -------
    dict
        Standardized success response containing the newly created task.

    Raises
    ------
    HTTPException
        Propagated from dependencies or the service layer if authentication
        fails or task creation cannot be completed.
    """

    # Delegate task creation to the service layer.
    new_task = task_service.create_task(task, user.id, db)

    return success_response(
        data=new_task,
        message="Task created successfully",
    )


@router.get("/")
def get_tasks(
    search: str | None = Query(None, description="Search tasks by title"),
    completed: bool | None = Query(None, description="Filter by completion status"),
    sort_by: str = Query("created_at", description="Field used for sorting"),
    order: str = Query("desc", description="Sorting order: asc or desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a paginated list of tasks belonging to the authenticated user.

    The endpoint supports advanced querying capabilities including:

    - Title-based search
    - Filtering by completion status
    - Sorting by supported fields
    - Pagination controls

    Only tasks owned by the authenticated user are returned.

    Parameters
    ----------
    search : str | None
        Optional keyword used for case-insensitive filtering by task title.

    completed : bool | None
        Optional filter for task completion status.

    sort_by : str
        Field used to sort the results.

    order : str
        Sorting direction. Accepted values are "asc" or "desc".

    skip : int
        Number of records skipped before returning results.

    limit : int
        Maximum number of tasks returned in the response.

    user : User
        Authenticated user injected by the authentication dependency.

    db : Session
        SQLAlchemy database session provided by FastAPI.

    Returns
    -------
    dict
        Standardized success response containing the filtered and
        paginated task collection.
    """

    # Delegate task retrieval to the service layer.
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
    Retrieve a specific task by its identifier.

    The task will only be returned if it exists and belongs to the
    authenticated user.

    Parameters
    ----------
    task_id : int
        Unique identifier of the requested task.

    user : User
        Authenticated user injected by the authentication dependency.

    db : Session
        SQLAlchemy database session provided by FastAPI.

    Returns
    -------
    dict
        Standardized success response containing the requested task.

    Raises
    ------
    HTTPException
        Raised if the task does not exist or does not belong to
        the authenticated user.
    """

    # Delegate single-task retrieval to the service layer.
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
    Update an existing task owned by the authenticated user.

    Partial updates are supported, meaning only the fields provided
    in the request body will be modified.

    Parameters
    ----------
    task_id : int
        Identifier of the task to update.

    task : TaskUpdate
        Payload containing fields to update.

    user : User
        Authenticated user injected by the authentication dependency.

    db : Session
        SQLAlchemy database session provided by FastAPI.

    Returns
    -------
    dict
        Standardized success response containing the updated task.

    Raises
    ------
    HTTPException
        Raised if the task does not exist or does not belong to
        the authenticated user.
    """

    # Delegate update operation to the service layer.
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
    Delete a task owned by the authenticated user.

    The task is permanently removed from the database if it exists
    and belongs to the requesting user.

    Parameters
    ----------
    task_id : int
        Identifier of the task to delete.

    user : User
        Authenticated user injected by the authentication dependency.

    db : Session
        SQLAlchemy database session provided by FastAPI.

    Returns
    -------
    dict
        Standardized success response confirming successful deletion.

    Raises
    ------
    HTTPException
        Raised if the task does not exist or does not belong to
        the authenticated user.
    """

    # Delegate deletion to the service layer.
    task_service.delete_task(task_id, user.id, db)

    return success_response(
        message="Task deleted successfully",
    )
