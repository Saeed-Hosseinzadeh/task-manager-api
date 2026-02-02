from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    """
    SQLAlchemy model representing a registered user in the system.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Relationship: One user can have multiple tasks
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(username={self.username}, email={self.email})>"


class Task(Base):
    """
    SQLAlchemy model representing a task created by a user.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)

    # Status and Metadata
    is_completed = Column(Boolean, default=False)
    priority = Column(Integer, default=1)  # 1: Low, 2: Medium, 3: High
    created_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)

    # Foreign Key linking to the User model
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationship: Each task belongs to a single owner
    owner = relationship("User", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task(title={self.title}, is_completed={self.is_completed})>"
