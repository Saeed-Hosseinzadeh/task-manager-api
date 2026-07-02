# Task Manager API

A production-oriented task management API built with **FastAPI**, **SQLAlchemy 2.0**, and **Pydantic v2**.

The project is structured around a clean service-oriented architecture with explicit separation between routing, business logic, persistence, validation, authentication, and infrastructure concerns. It provides user authentication, task management, consistent API responses, structured logging, and centralized exception handling in a codebase designed to stay maintainable as it grows.

---

## Features

- Clean FastAPI application structure with focused modules and predictable responsibilities
- Modern SQLAlchemy 2.0 model definitions using typed mappings
- Pydantic v2 schemas for request validation and response serialization
- JWT-based authentication with **access** and **refresh** tokens
- Password hashing via **Passlib** using **PBKDF2-SHA256**
- Reusable service layer for auth and task workflows
- Consistent API response shape across endpoints
- Centralized global exception handling for HTTP, validation, and database errors
- Structured logging to both **console** and `logs/app.log`
- Test-friendly design with clear dependency boundaries

---

## Tech Stack

- **Python 3.13**
- **FastAPI**
- **SQLAlchemy** (ORM)
- **Pydantic v2**
- **Passlib** with **PBKDF2-SHA256**
- **python-jose** for JWT handling
- **Uvicorn** for local development server

---

## Project Structure

```text
task_manager_api/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── routers/
│   │   ├── auth.py
│   │   └── tasks.py
│   ├── services/
│   │   ├── auth_service.py
│   │   └── task_service.py
│   ├── utils/
│   │   ├── exceptions.py
│   │   ├── logger.py
│   │   └── response.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests/
├── alembic/
├── .env.example
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

---

## Architecture Overview

The application is organized around a small set of clear layers:

- **Routers** define HTTP endpoints and request/response flow
- **Services** contain business logic and keep route handlers thin
- **Models** define database entities using SQLAlchemy 2.0 typed mappings
- **Schemas** validate input and serialize output with Pydantic v2
- **Dependencies** encapsulate shared FastAPI dependency logic such as authentication and database sessions
- **Core** contains configuration and security primitives
- **Utils** provide response formatting, logging, and exception handling

This structure keeps framework details from bleeding into business logic and makes testing and refactoring straightforward.

---

## Authentication

Authentication is based on JWT tokens and follows a simple split:

- **Access token** for authenticated API requests
- **Refresh token** for obtaining a new access token without forcing the user to log in again

Security-related behavior includes:

- Password hashing with **PBKDF2-SHA256**
- Token creation with explicit expiration
- Token type validation (`access` vs `refresh`)
- Current-user resolution through a dedicated FastAPI dependency

---

## Logging and Error Handling

The API includes centralized operational concerns out of the box:

### Structured Logging

- Logs are written to both:
  - standard output
  - `logs/app.log`
- Uses a clean, production-friendly format suitable for local development and deployment environments

### Global Exception Handling

- HTTP errors are normalized into a consistent response structure
- Request validation errors are returned with useful field-level details
- SQLAlchemy exceptions are logged without leaking internal database details
- Unhandled exceptions fall back to a safe internal server error response

---

## API Response Shape

The API uses a consistent response wrapper for both successful and failed operations.

### Success response

```json
{
  "success": true,
  "message": "Task created successfully",
  "data": {
    "id": 1,
    "title": "Write README",
    "is_completed": false
  }
}
```

### Error response

```json
{
  "success": false,
  "message": "Input validation failed",
  "data": [
    {
      "field": "title",
      "message": "Field required"
    }
  ]
}
```

This keeps client integration predictable and reduces ad hoc response formatting across endpoints.

---

## Setup and Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd task_manager_api
```

### 2. Create and activate a virtual environment

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root. Use `.env.example` as the starting point.

Typical values include database connection settings, JWT secret configuration, and token expiration settings.

### 5. Run the application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## Development Notes

### Database

The project uses SQLAlchemy as the ORM and is designed around modern typed model declarations. Depending on your current setup, you can point the application at SQLite for local development or another relational database via environment configuration.

### Testing

If test files are present, run them with:

```bash
pytest
```

### Health Check

A simple health endpoint is exposed for service monitoring:

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

---

## API Modules

### Auth

Authentication endpoints are responsible for:

- user registration
- login
- refresh token exchange

### Tasks

Task endpoints support:

- creating tasks
- listing tasks
- retrieving a single task
- updating tasks
- deleting tasks

Filtering and sorting behavior is handled in the service layer to keep route handlers concise.

---

## Why This Structure Works

This codebase is intentionally optimized for maintainability rather than cleverness.

- Route handlers remain thin and readable
- Business rules live in services
- Validation rules live in schemas
- Database concerns stay close to models and session dependencies
- Operational concerns such as logging and exception handling are centralized

That balance makes the project easy to reason about, extend, and test in a real production workflow.

---

## Running in Production

For production deployment:

- run with a proper ASGI server process setup
- replace permissive CORS settings with explicit allowed origins
- provide a strong `SECRET_KEY`
- configure environment variables explicitly
- route logs to your platform’s aggregation stack if needed

---

## License

This project is distributed under the terms defined in the repository license.
