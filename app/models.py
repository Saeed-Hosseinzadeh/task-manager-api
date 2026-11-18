from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, false, text
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import FunctionElement

from app.database import Base


class UTCWallTime(FunctionElement[datetime]):
    type = DateTime()
    inherit_cache = True


@compiles(UTCWallTime, "postgresql")
def compile_postgresql_utc_wall_time(element, compiler, **kwargs):
    return "(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"


@compiles(UTCWallTime)
def compile_utc_wall_time(element, compiler, **kwargs):
    return "CURRENT_TIMESTAMP"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    tasks: Mapped[list[Task]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username!r})"


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint(
            "due_date IS NULL OR due_date_instant IS NULL",
            name="ck_tasks_single_due_date",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_completed: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false(), nullable=False
    )
    priority: Mapped[int] = mapped_column(default=1, server_default=text("1"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        server_default=UTCWallTime(),
        nullable=False,
    )
    legacy_due_date: Mapped[datetime | None] = mapped_column("due_date", DateTime())
    due_date_instant: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    @property
    def due_date(self) -> datetime | None:
        instant = self.due_date_instant
        if instant is None:
            return self.legacy_due_date
        # SQLite stores UTC instants without a timezone offset.
        if instant.tzinfo is None:
            return instant.replace(tzinfo=UTC)
        return instant.astimezone(UTC)

    @due_date.setter
    def due_date(self, value: datetime | None) -> None:
        if value is not None and value.utcoffset() is None:
            raise ValueError("A new deadline must include a timezone offset")
        self.legacy_due_date = None
        self.due_date_instant = value.astimezone(UTC) if value is not None else None

    # Foreign Keys & Relationships
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner: Mapped[User] = relationship(back_populates="tasks")

    def __repr__(self) -> str:
        return f"Task(id={self.id}, title={self.title!r}, is_completed={self.is_completed})"
