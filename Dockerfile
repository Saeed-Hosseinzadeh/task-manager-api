FROM python:3.11-slim

# Prevent python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure logs are flushed immediately
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Install system dependencies (optional but useful)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first to leverage Docker cache
COPY requirements.txt /tmp/requirements.txt

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Create non-root user for security
RUN adduser --disabled-password --gecos "" appuser

# Copy application code
COPY . /code

# Change ownership to the non-root user
RUN chown -R appuser:appuser /code

# Switch to non-root user
USER appuser

# Run FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
