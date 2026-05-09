"""
Main Application Entry Point

This module serves as the entry point for the FastAPI application.
It handles environment path configuration, router registration,
and initializes the API instance.
"""

from fastapi import FastAPI
import sys
import os

# Add current directory to sys.path to ensure correct module resolution in CI/CD environments.
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

try:
    # Attempt to import routers when the application is structured under the 'app' module.
    from routers import auth, tasks
except ImportError:
    # Fallback import for when the application is executed from the project root directory.
    from app.routers import auth, tasks

# Create FastAPI application instance
app = FastAPI(
    title="Task Manager API",
    version="1.0.0",
    description="A simple task management API with authentication support."
)

# ---------------------------------------------------------
# Health Check Route
# ---------------------------------------------------------
@app.get("/health", tags=["Health"])
def health_check():
    """
    Verify the API service availability.

    Returns:
        dict: A status dictionary confirming the API is operational.
    """
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
