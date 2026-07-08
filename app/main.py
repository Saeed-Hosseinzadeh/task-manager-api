from __future__ import annotations

from fastapi import FastAPI

from app.routers import auth, tasks
from app.schemas import HealthResponse
from app.utils.response import success_response

app = FastAPI()

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health", tags=["Health"], response_model=HealthResponse)
def health_check() -> dict:
    return success_response(
        data={"status": "ok"},
        message="Service is healthy",
    )
