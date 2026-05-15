# 🚀 Task Manager API

A production‑style **Task Management REST API** built with **FastAPI**, demonstrating clean architecture, secure authentication, automated testing, and containerized deployment.

This repository is designed as a **portfolio‑grade backend project** that showcases modern Python backend engineering practices.

---

## 🛡️ Badges

[![CI/CD Pipeline](https://github.com/Saeed-Hosseinzadeh/task-manager-api/actions/workflows/ci.yml/badge.svg)](https://github.com/Saeed-Hosseinzadeh/task-manager-api/actions)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-production-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![Tests](https://img.shields.io/badge/tests-pytest-success)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## 📌 Why This Project Exists

This project demonstrates how to build a **realistic backend service** using modern Python tools and production‑style engineering practices.

**The goals of this project are:**
- Demonstrate clean backend architecture
- Implement secure authentication with JWT
- Showcase database migrations
- Provide automated testing
- Demonstrate containerized deployment
- Provide clear developer documentation

**It can serve as:**
- A backend architecture reference
- A learning resource for FastAPI
- A portfolio project for backend roles

---

## ✨ Key Features

- **User Authentication:** Registration and authentication flows.
- **Secure Access:** JWT access tokens and password hashing with Passlib.
- **Task Management:** Full CRUD operations for tasks.
- **Database:** PostgreSQL database integration with SQLAlchemy 2.0 ORM.
- **Migrations:** Version control for database schemas using Alembic.
- **Configuration:** Environment‑based configuration management.
- **Containerization:** Dockerized development environment.
- **Testing:** Automated testing with pytest.
- **Documentation:** Interactive API documentation out of the box.

---

## 🛠️ Technology Stack

| Category | Technology |
| :--- | :--- |
| **Framework** | FastAPI |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy 2.0 |
| **Migrations** | Alembic |
| **Authentication** | JWT (`python‑jose`) |
| **Security** | Passlib (Password hashing) |
| **Configuration** | Pydantic Settings |
| **Testing** | Pytest + HTTPX |
| **Containerization** | Docker / Docker Compose |

---

## 🏗️ Architecture

The project follows a **layered architecture** to keep responsibilities separated and maintainable.
```text
Client
  │
  ▼
API Layer (FastAPI Routers)
  │
  ▼
Service Layer (Business Logic)
  │
  ▼
Data Layer (SQLAlchemy Models)
  │
  ▼
PostgreSQL Database

- **API Layer:** Handles HTTP requests and responses.
- **Service Layer:** Contains application business logic.
- **Data Layer:** Manages persistence and database interaction.

---

## 📁 Project Structure

Each layer has a clear responsibility which keeps the codebase scalable and easy to maintain.

text
app/
├── api/
│   └── routers/
│       ├── auth.py
│       └── tasks.py
├── core/
│   ├── config.py
│   ├── security.py
│   └── logger.py
├── db/
│   └── database.py
├── models/
│   └── models.py
├── schemas/
│   └── schemas.py
├── services/
│   ├── auth_service.py
│   └── task_service.py
└── main.py

alembic/
tests/
├── conftest.py
├── test_auth.py
└── test_tasks.py

---

## ⚙️ Environment Variables

Create a `.env` file using `.env.example` as a reference. Example configuration:

env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/task_db
SECRET_KEY=super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

**Variable Descriptions:**
- `DATABASE_URL`: Database connection string used by SQLAlchemy.
- `SECRET_KEY`: Secret used for signing JWT tokens.
- `ALGORITHM`: JWT hashing algorithm.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Expiration time for access tokens.
- `REFRESH_TOKEN_EXPIRE_DAYS`: Expiration time for refresh tokens.

---

## 🚀 Running the Application

**Run locally:**
bash
uvicorn app.main:app --reload
Application will be available at: `http://localhost:8000`

---

## 🐳 Docker Deployment

Run the entire stack with Docker (Starts FastAPI API server & PostgreSQL database):
bash
docker-compose up --build

Stop containers:
bash
docker-compose down

---

## 🗄️ Database Migrations

Apply migrations:
bash
alembic upgrade head

Create a new migration:
bash
alembic revision --autogenerate -m "new migration"

---

## 📚 API Documentation

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📡 API Endpoints

**Authentication**
- `POST /auth/register`
- `POST /auth/login`

**Tasks**
- `POST /tasks`
- `GET /tasks`
- `GET /tasks/{id}`
- `DELETE /tasks/{id}`

---

## 💻 Sample Requests / Responses

### 1. Register
**Request:** `POST /auth/register`
json
{
  "username": "john",
  "email": "john@example.com",
  "password": "StrongPassword123"
}
**Response:**
json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
"id": 1,
"email": "john@example.com"
  }
}

### 2. Login
**Request:** `POST /auth/login`
json
{
  "identifier": "john@example.com",
  "password": "StrongPassword123"
}
**Response:**
json
{
  "success": true,
  "data": {
"access_token": "...",
"refresh_token": "..."
  }
}

### 3. Create Task
**Request:** `POST /tasks`
*Headers: `Authorization: Bearer <access_token>`*
json
{
  "title": "Complete project",
  "description": "Finish implementing the API"
}

---

## 📸 Screenshots / Demo

*(Example responses can be viewed directly in the interactive documentation at the `/docs` endpoint. You can add screenshots from Swagger UI here for demonstration.)*

---

## 🔄 Continuous Integration

Example GitHub Actions pipeline:
- Install dependencies
- Run lint checks
- Run tests

*(CI badge is included at the top of this document).*

---

## ✔️ Testing

Run all tests:
bash
pytest
Verbose mode:
bash
pytest -vv
**Tests cover:** Authentication flow, token generation, protected endpoints, and task creation.

---

## 🚧 Troubleshooting

- **Database connection issues:** Verify PostgreSQL is running and `DATABASE_URL` is correct.
- **Docker issues:** Run `docker-compose logs` to see detailed errors.
- **Migration errors:** Ensure the database exists before running migrations.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push branch
5. Open pull request

---

## 🗺️ Roadmap

Possible future improvements:
- [ ] Refresh token rotation
- [ ] Task update endpoint
- [ ] Pagination support
- [ ] Role based authorization
- [ ] Rate limiting
- [ ] Production deployment example

---

## 📄 License

MIT License - [https://opensource.org/licenses/MIT](https://opensource.org/licenses/MIT)