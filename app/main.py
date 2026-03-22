"""
Main Application Entry Point

This module initializes the FastAPI application and registers all routers.
Optimized for both Local and GitHub Actions environments.
"""

from fastapi import FastAPI
import sys
import os

# اضافه کردن مسیر جاری به پایتون برای حل مشکل ایمپورت در CI
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

try:
    # سعی برای ایمپورت زمانی که در پوشه app هستیم
    from routers import auth, tasks
except ImportError:
    # سعی برای ایمپورت زمانی که از روت پروژه اجرا می‌شود
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
    """Verify API availability."""
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
