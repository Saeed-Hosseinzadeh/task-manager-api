# 🚀 Task Manager API (Modern & Scalable)

A professional, asynchronous Task Management REST API built with **FastAPI**, **SQLAlchemy 2.0**, and **PostgreSQL**. This project is fully containerized with **Docker** and follows industry best practices for backend development, including layered architecture, automated testing, and secure authentication.

---

## 🌟 Key Features

- **Asynchronous Core:** High-performance request handling using FastAPI and asyncpg.
- **Layered Architecture:** Clean separation of concerns (Routers, Services, Utils, Models).
- **Secure Auth:** JWT-based (OAuth2) authentication with password hashing using Passlib.
- **Database Migrations:** Managed by Alembic for seamless schema evolution.
- **Enterprise Dockerization:** Multi-stage builds and health checks.
- **Centralized Logging & Exception Handling:** Structured logs and global error management.
- **Automated Testing:** Comprehensive test suite using Pytest and httpx.

---

## 🏗️ Technical Stack

| Category | Technology |
|-----------|------------|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Migration | Alembic |
| Containerization | Docker & Docker Compose |
| Testing | Pytest |
| Security | JWT, OAuth2, Bcrypt |

---

## 📂 Project Structure

```
├── app/
│   ├── core/
│   ├── routers/
│   ├── services/
│   ├── utils/
│   ├── database.py
│   ├── dependencies.py
│   ├── models.py
│   ├── schemas.py
│   └── main.py
├── alembic/
├── tests/
├── logs/
├── .env.example
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
└── pytest.ini
```

---

## 🚦 Getting Started

### 1. Setup Environment
```bash
cp .env.example .env
```

### 2. Run with Docker
```bash
docker-compose up -d --build
```

### 3. Initialize Database
```bash
docker-compose exec web alembic upgrade head
```

---

## 🧪 Testing & Documentation

### Interactive API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Run Tests
```bash
docker-compose exec web pytest
```

---

## 🛠️ Architecture Notes

- Business logic lives in the `services/` layer.
- Centralized exception handling ensures consistent API responses.
- OAuth2PasswordBearer secures protected routes.
- Alembic autogenerate keeps DB schema synchronized.

---

## 📄 License

MIT License
