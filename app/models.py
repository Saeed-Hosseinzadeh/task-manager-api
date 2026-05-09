"""
Database Models

This module defines the SQLAlchemy models for the application, establishing the
relational data structure for Users and their associated Tasks.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    """
    User model representing a registered user in the system.

    Attributes:
        id (int): Primary key for the user.
        username (str): Unique username for authentication.
        email (str): Unique email address of the user.
        hashed_password (str): Securely hashed password.
        tasks (relationship): Relationship to Task models owned by this user.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Relationship: One user can have multiple tasks
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """Returns a string representation of the User object."""
        return f"<User(username={self.username}, email={self.email})>"


class Task(Base):
    """
    Task model representing a task created by a user.

    Attributes:
        id (int): Primary key for the task.
        title (str): The title of the task.
        description (str): Detailed description of the task.
        is_completed (bool): Completion status of the task.
        priority (int): Priority level (1: Low, 2: Medium, 3: High).
        created_at (datetime): Timestamp when the task was created.
        due_date (datetime): Deadline for the task.
        owner_id (int): Foreign key referencing the user who owns the task.
        owner (relationship): The User object associated with this task.
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
        """Returns a string representation of the Task object."""
        return f"<Task(title={self.title}, is_completed={self.is_completed})>"
