"""Align the published PostgreSQL schema with the ORM models.

Legacy timestamps are preserved as stored. New deadlines use a separate
timezone-aware column. Missing creation times receive the migration transaction
time as UTC wall time. Missing completion and priority use the application
defaults. The migration never guesses an owner or truncates data.
"""

from alembic import op
import sqlalchemy as sa

revision = "ef72b89db261"
down_revision = "9aa2a41540d5"
branch_labels = None
depends_on = None

STRING_COLUMNS = {
    "users": {"username": 50, "hashed_password": 255},
    "tasks": {"title": 150, "description": 500},
}
UTC_WALL_TIME = "(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"
DUE_DATE_CHECK = "ck_tasks_single_due_date"
OWNER_FK = "tasks_owner_id_fkey"


def require_postgresql() -> None:
    if op.get_context().dialect.name != "postgresql":
        raise RuntimeError("This revision requires PostgreSQL; use ORM metadata for fast SQLite tests.")


def upgrade() -> None:
    require_postgresql()
    op.execute("LOCK TABLE users, tasks IN ACCESS EXCLUSIVE MODE")
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM tasks WHERE owner_id IS NULL) THEN
                RAISE EXCEPTION 'Tasks without an owner must be resolved before upgrading';
            END IF;
        END;
        $$;
    """)
    for table, columns in STRING_COLUMNS.items():
        for column, length in columns.items():
            op.execute(f"""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM {table} WHERE char_length({column}) > {length}
                    ) THEN
                        RAISE EXCEPTION '{table}.{column} exceeds the new length limit';
                    END IF;
                END;
                $$;
            """)
            op.alter_column(table, column, type_=sa.String(length), existing_type=sa.String())

    op.add_column("tasks", sa.Column("due_date_instant", sa.DateTime(timezone=True)))
    op.create_check_constraint(
        DUE_DATE_CHECK, "tasks", "due_date IS NULL OR due_date_instant IS NULL"
    )
    op.execute(f"UPDATE tasks SET created_at = {UTC_WALL_TIME} WHERE created_at IS NULL")
    op.execute("UPDATE tasks SET is_completed = false WHERE is_completed IS NULL")
    op.execute("UPDATE tasks SET priority = 1 WHERE priority IS NULL")
    op.alter_column("tasks", "created_at", nullable=False, server_default=sa.text(UTC_WALL_TIME))
    op.alter_column("tasks", "is_completed", nullable=False, server_default=sa.false())
    op.alter_column("tasks", "priority", nullable=False, server_default=sa.text("1"))
    op.alter_column("tasks", "owner_id", nullable=False)

    op.drop_constraint(OWNER_FK, "tasks", type_="foreignkey")
    op.create_foreign_key(OWNER_FK, "tasks", "users", ["owner_id"], ["id"], ondelete="CASCADE")
    op.create_index(op.f("ix_tasks_owner_id"), "tasks", ["owner_id"])


def downgrade() -> None:
    require_postgresql()
    op.execute("LOCK TABLE tasks IN ACCESS EXCLUSIVE MODE")
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM tasks WHERE due_date_instant IS NOT NULL) THEN
                RAISE EXCEPTION 'Downgrade would discard timezone-aware deadlines; export or resolve them first';
            END IF;
        END;
        $$;
    """)
    op.drop_index(op.f("ix_tasks_owner_id"), table_name="tasks")
    op.drop_constraint(OWNER_FK, "tasks", type_="foreignkey")
    op.create_foreign_key(OWNER_FK, "tasks", "users", ["owner_id"], ["id"])
    op.alter_column("tasks", "owner_id", nullable=True)
    for column in ("created_at", "is_completed", "priority"):
        op.alter_column("tasks", column, nullable=True, server_default=None)

    op.drop_constraint(DUE_DATE_CHECK, "tasks", type_="check")
    op.drop_column("tasks", "due_date_instant")
    for table, columns in STRING_COLUMNS.items():
        for column, length in columns.items():
            op.alter_column(table, column, type_=sa.String(), existing_type=sa.String(length))
