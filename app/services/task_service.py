from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Task, User
from app.schemas import TaskCreate, TaskUpdate


def create_task(task_data: TaskCreate, user_id: int, db: Session) -> Task:
    task = Task(
        title=task_data.title,
        description=task_data.description,
        is_completed=task_data.is_completed,
        priority=task_data.priority,
        due_date=task_data.due_date,
        owner_id=user_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_user_tasks(
    db: Session,
    user_id: int,
    completed: bool | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> list[Task]:
    query = db.query(Task).filter(Task.owner_id == user_id)

    if completed is not None:
        query = query.filter(Task.is_completed == completed)

    sort_columns = {
        "created_at": Task.created_at,
        "title": Task.title,
        "is_completed": Task.is_completed,
    }
    sort_column = sort_columns.get(sort_by)
    if sort_column is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort field",
        )

    if sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    return query.all()


def get_task_by_id(task_id: int, user_id: int, db: Session) -> Task:
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.owner_id == user_id)
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


def update_task(task_id: int, task_data: TaskUpdate, user_id: int, db: Session) -> Task:
    task = get_task_by_id(task_id, user_id, db)

    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task(task_id: int, user_id: int, db: Session) -> None:
    task = get_task_by_id(task_id, user_id, db)
    db.delete(task)
    db.commit()


def get_task_owner(user_id: int, db: Session) -> User | None:
    return db.query(User).filter(User.id == user_id).first()
