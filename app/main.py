"""
Main Application Entry Point

This module initializes the FastAPI application and registers all routers
used by the API.

Using relative imports to ensure compatibility between local development
and CI/CD environments (GitHub Actions).
"""

from fastapi import FastAPI

# Using relative imports to avoid PYTHONPATH issues in CI
try:
    from .routers import auth, tasks
except ImportError:
    # Fallback for different execution contexts
    from app.routers import auth, tasks


# Create FastAPI application instance
app = FastAPI(
    title="Task Manager API",
    version="1.0.0",
    description="A simple task management API with authentication support."
)


# ---------------------------------------------------------
# Health Check Route (For CI/CD Verification)
# ---------------------------------------------------------
@app.get("/health", tags=["Health"])
def health_check():
    """Verify that the API application is running and accessible."""
    return {"status": "ok"}


# ---------------------------------------------------------
# Authentication Routes
# ---------------------------------------------------------
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)


# ---------------------------------------------------------
# Task Routes
# ---------------------------------------------------------
app.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["Tasks"]
)
