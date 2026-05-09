# -----------------------------------------------------------------------------
# Dockerfile for FastAPI Task Manager Application
#
# This Dockerfile builds a lightweight production-ready container image
# for the FastAPI application. It uses the official Python slim image,
# installs required dependencies, and runs the application using Uvicorn.
#
# Key Design Choices
# ------------------
# - Uses a minimal base image to reduce attack surface and image size
# - Installs dependencies before copying application code to leverage caching
# - Runs the application using a non-root user for improved security
# - Disables Python bytecode generation and enables unbuffered logging
# -----------------------------------------------------------------------------

FROM python:3.11-slim

# Prevent Python from generating .pyc files inside the container
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure logs are written immediately (useful for container logging systems)
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /code

# -----------------------------------------------------------------------------
# Install minimal system dependencies
#
# curl is included for container health checks and debugging purposes.
# The apt cache is removed afterward to keep the image small.
# -----------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Dependency Installation
#
# Copying the requirements file first allows Docker to cache the dependency
# layer. This significantly speeds up rebuilds when application code changes
# but dependencies remain the same.
# -----------------------------------------------------------------------------
COPY requirements.txt /tmp/requirements.txt

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# -----------------------------------------------------------------------------
# Security: Create a non-root user
#
# Running containers as a non-root user is a recommended security practice
# that reduces the potential impact of container compromises.
# -----------------------------------------------------------------------------
RUN adduser --disabled-password --gecos "" appuser

# Copy the application source code into the container
COPY . /code

# Assign ownership of application files to the non-root user
RUN chown -R appuser:appuser /code

# Switch to the non-root user for runtime
USER appuser

# -----------------------------------------------------------------------------
# Application Startup
#
# Launch the FastAPI application using Uvicorn ASGI server.
# The application is exposed on port 8000.
# -----------------------------------------------------------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
