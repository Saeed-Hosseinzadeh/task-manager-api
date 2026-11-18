from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import (
    EmptyResponse,
    TaskCreate,
    TaskDetailResponse,
    TaskListResponse,
    TaskUpdate,
)
from app.services.task_service import (
    create_task,
    delete_task,
    get_task_by_id,
    get_user_tasks,
    update_task,
)
from app.utils.response import success_response

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TaskDetailResponse)
def create(
    task: TaskCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    result = create_task(task, user.id, db)
    return success_response(
        data=result,
        message="Task created successfully",
    )


@router.get("/", response_model=TaskListResponse)
def list_tasks(
    completed: bool | None = Query(default=None),
    sort_by: Literal["created_at", "title", "is_completed"] = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
    priority: int | None = Query(default=None, ge=1, le=5),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=2_147_483_647),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    result = get_user_tasks(
        db=db,
        user_id=user.id,
        completed=completed,
        sort_by=sort_by,
        sort_order=sort_order,
        priority=priority,
        limit=limit,
        offset=offset,
    )
    return success_response(
        data=result,
        message="Tasks retrieved successfully",
    )


@router.get("/{task_id}", response_model=TaskDetailResponse)
def get_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    result = get_task_by_id(task_id, user.id, db)
    return success_response(
        data=result,
        message="Task retrieved successfully",
    )


@router.put("/{task_id}", response_model=TaskDetailResponse)
def update(
    task_id: int,
    task: TaskUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    result = update_task(task_id, task, user.id, db)
    return success_response(
        data=result,
        message="Task updated successfully",
    )


@router.delete("/{task_id}", response_model=EmptyResponse)
def delete_task_endpoint(
    task_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    delete_task(task_id, user.id, db)
    return success_response(
        data=None,
        message="Task deleted successfully",
    )
