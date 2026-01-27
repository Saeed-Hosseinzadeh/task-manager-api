from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from fastapi import HTTPException

from app.models import Task


def create_task(task_data, user_id, db: Session):

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
    user_id,
    db: Session,
    search: str = None,
    completed: bool = None,
    sort_by: str = "created_at",
    order: str = "desc",
    skip: int = 0,
    limit: int = 10
):

    query = db.query(Task).filter(Task.owner_id == user_id)

    if search:
        query = query.filter(Task.title.contains(search))

    if completed is not None:
        query = query.filter(Task.is_completed == completed)

    sort_column = getattr(Task, sort_by, Task.created_at)

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


def get_task(task_id, user_id, db: Session):

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == user_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


def update_task(task_id, user_id, task_data, db: Session):

    task = get_task(task_id, user_id, db)

    update_data = task_data.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


def delete_task(task_id, user_id, db: Session):

    task = get_task(task_id, user_id, db)

    db.delete(task)
    db.commit()

    return {"message": "Task deleted"}
