"""
Main Application Entry Point

This module initializes the FastAPI application and registers all routers
used by the API.

Routers are mounted here with prefixes to keep route management centralized
and prevent duplication.

The module also exposes a lightweight health-check endpoint that can be used
by CI/CD pipelines, monitoring tools, Docker health checks, and automated tests
to verify that the FastAPI application is running correctly.
"""

from fastapi import FastAPI

# Import API routers
from app.routers import auth
from app.routers import tasks


# Create FastAPI application instance
app = FastAPI(
    title="Task Manager API",
    version="1.0.0",
    description="A simple task management API with authentication support."
)


# ---------------------------------------------------------
# Health Check Route
# ---------------------------------------------------------
# This endpoint is intentionally simple and does not require
# authentication or database access.
#
# It is useful for:
# - GitHub Actions CI checks
# - Docker/container health checks
# - Load balancer health checks
# - Basic API availability checks
#
# Example:
# GET /health
# Response:
# {
#     "status": "ok"
# }
# ---------------------------------------------------------
@app.get("/health", tags=["Health"])
def health_check():
    """
    Check whether the API application is running.

    This endpoint returns a simple success response when the FastAPI
    application is available. It does not check database connectivity
    because its main purpose is to confirm that the application itself
    has started successfully.

    Returns:
        dict: A dictionary containing the application health status.
    """
    return {"status": "ok"}


# ---------------------------------------------------------
# Authentication Routes
# ---------------------------------------------------------
# All authentication routes will start with /auth
#
# Example:
# POST /auth/register
# POST /auth/login
# POST /auth/refresh
# ---------------------------------------------------------
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)


# ---------------------------------------------------------
# Task Routes
# ---------------------------------------------------------
# Example routes:
#
# GET    /tasks
# POST   /tasks
# PUT    /tasks/{id}
# DELETE /tasks/{id}
# ---------------------------------------------------------
app.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["Tasks"]
)
