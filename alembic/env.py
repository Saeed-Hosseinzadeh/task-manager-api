"""
Alembic Migration Environment

This module configures the Alembic migration environment for the
application. It provides the necessary setup for running database
migrations in both offline and online modes.

Purpose
-------
- Load application configuration
- Expose SQLAlchemy metadata for migration autogeneration
- Configure Alembic migration context
- Execute migrations using either a database connection or a URL

Migration Modes
---------------
Offline Mode
    Migrations are generated without creating a database engine.
    SQL statements are emitted directly using the configured
    database URL.

Online Mode
    Migrations are executed against a live database connection
    using the application's SQLAlchemy engine.

Autogeneration
--------------
Alembic's autogenerate feature relies on the application's SQLAlchemy
models. Importing `app.models` ensures that all model classes are
registered in the metadata registry.
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context


# Ensure the project root directory is included in Python's module search path.
# This allows Alembic to correctly locate and import the application's modules.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from app.database import Base
from app.core.config import settings
import app.models  # Ensures models are registered for Alembic autogeneration


# Alembic configuration object providing access to values from alembic.ini.
config = context.config


# Configure Python logging using the configuration defined in alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# SQLAlchemy metadata used by Alembic's autogenerate feature to detect schema changes.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run database migrations in offline mode.

    In offline mode, Alembic does not create a database engine or
    establish a live database connection. Instead, migrations are
    generated using only the database URL and SQL statements are
    emitted directly.

    This mode is useful for environments where database connectivity
    is unavailable or when generating migration scripts.
    """
    url = settings.DATABASE_URL

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run database migrations in online mode.

    In this mode, Alembic connects to the database using the
    application's SQLAlchemy engine. Migrations are executed
    directly against the database within a transactional context.
    """

    # Import the application's configured SQLAlchemy engine.
    # The engine is defined in the database module and reused here
    # to ensure consistent configuration across the application.
    from app.database import engine

    # Establish a database connection and associate it with Alembic.
    with engine.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True
        )

        # Execute migrations inside a transactional scope.
        with context.begin_transaction():
            context.run_migrations()


# Determine migration mode based on Alembic's execution context.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
