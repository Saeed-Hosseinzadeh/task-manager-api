# Task Manager API

A FastAPI service for user-owned tasks. It uses Python 3.11, PostgreSQL,
SQLAlchemy 2, Alembic, Pydantic 2, PBKDF2-SHA256 password hashing, and signed JWTs.
Routers handle HTTP, services implement task and authentication workflows, and
`app/database.py` manages a session per request. Database schema changes live in
`alembic/versions/`.

## Start with Docker Compose

Install Docker with Linux containers, Compose v2, and Python 3.11 or newer for
the secret-generation command. From the repository root, create a local
`.env` if one does not already exist:

```powershell
if (-not (Test-Path .env)) {
    $jwt = python -c "import secrets; print(secrets.token_hex(32))"
    $db = python -c "import secrets; print(secrets.token_hex(24))"
    @("SECRET_KEY=$jwt", "POSTGRES_PASSWORD=$db") | Set-Content -Encoding ascii .env
}
docker compose up --build --wait --wait-timeout 120
curl.exe --fail http://127.0.0.1:8000/health
```

For a POSIX shell:

```sh
test ! -e .env && (
  umask 077
  jwt=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  db=$(python3 -c "import secrets; print(secrets.token_hex(24))")
  printf 'SECRET_KEY=%s\nPOSTGRES_PASSWORD=%s\n' "$jwt" "$db" > .env
)
docker compose up --build --wait --wait-timeout 120
curl --fail http://127.0.0.1:8000/health
```

Compose starts PostgreSQL 14, runs Alembic in a one-shot service, and starts the
web service after migration succeeds. The API binds to loopback on the host.
Open Swagger UI at [localhost:8000/docs](http://127.0.0.1:8000/docs) or ReDoc at
[localhost:8000/redoc](http://127.0.0.1:8000/redoc). Use `docker compose down`
to stop the services and retain the database volume. An existing volume
requires its initialized database password. Changing an environment variable
does not change the password stored in PostgreSQL.

## Run directly with Python

Create a Python 3.11 virtual environment and install the requirements. Start a
local PostgreSQL database and set `DATABASE_URL` to its connection URL. Set a
random `SECRET_KEY` through your environment or a local copy of `.env.example`.
Use a disposable database for development and testing.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

On a POSIX shell, create the environment with `python3.11 -m venv .venv`,
activate it with `. .venv/bin/activate`, and run the same install, migration,
and Uvicorn commands.

| Setting | Purpose |
| --- | --- |
| `DATABASE_URL` | PostgreSQL SQLAlchemy URL for direct runs. Compose supplies its internal URL using service host `db`. Percent-encode special characters in manually configured URLs. |
| `SECRET_KEY` | Required signing key of at least 32 characters. Generate a random value and keep it private. |
| `POSTGRES_PASSWORD` | Required by Compose. Use a hex string so it can be embedded in the Compose connection URL without escaping. |
| `ALGORITHM` | Optional, fixed to `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Positive integer, default `60`. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Positive integer, default `7`. |
| `ALLOWED_ORIGINS` | JSON array of explicitly allowed frontend origins. Defaults to an empty list. |
| `ENVIRONMENT` | `development`, `test`, or `production`. Defaults to `development`. |

Use HTTPS and rate limits for authentication routes at your deployment
boundary. Keep database and JWT credentials outside Git. Application errors
use console logging, and validation responses omit the input values.

## API and authentication

| Method and path | Request or behavior |
| --- | --- |
| `POST /auth/register` | JSON with `username`, `email`, and `password`. Returns the account and both tokens. |
| `POST /auth/login` | JSON with `identifier` (username or email) and `password`. Returns both tokens. |
| `POST /auth/refresh` | JSON with `refresh_token`. Returns a new access token for an existing account. |
| `POST /tasks/` | Creates a task for the authenticated user. `title` is required. |
| `GET /tasks/` | Lists the caller’s tasks. Optional parameters are `completed`, `sort_by` (`created_at`, `title`, `is_completed`), and `sort_order` (`asc`, `desc`). |
| `GET /tasks/{task_id}` | Returns a task owned by the caller. |
| `PUT /tasks/{task_id}` | Applies only the submitted fields. Explicit null clears `description` or `due_date`. |
| `DELETE /tasks/{task_id}` | Deletes a task owned by the caller. |
| `GET /health` | Returns application liveness. Compose separately gates startup on PostgreSQL and a successful migration. |

For task routes, send `Authorization: Bearer <access_token>`. Access tokens
and refresh tokens have distinct roles. Refresh tokens are reusable until
expiration while the account exists. Per-session rotation and revocation are
outside the current API contract.

Example authenticated request:

```http
POST /tasks/
Authorization: Bearer <access_token>
Content-Type: application/json

{"title":"Review release","priority":2,"due_date":"2026-11-18T15:30:00+03:30"}
```

Successful responses have `success`, `message`, and `data` fields.
The health response contains `"data":{"status":"ok"}`. Error responses use the
same envelope with `success: false`. Invalid credentials return `401` with
`WWW-Authenticate: Bearer`. Tasks outside the current user's ownership return
`404`, duplicate registration returns `409`, and invalid inputs return
`422` with field errors in `data`.

```json
{"success":false,"message":"Input validation failed","data":[{"field":"title","message":"Field required"}]}
```

## Migration and timestamp policy

Revision `ef72b89db261` preserves existing creation times and deadlines as
stored. Missing and newly generated `created_at` values use a UTC wall-clock
value in the existing timezone-free column. Missing completion and priority
values become `false` and `1`. Existing email capacity is preserved.

New or replaced deadlines require an ISO 8601 offset and are returned in UTC.
A legacy deadline is returned without an offset because its timezone is
unknown. Omitting a deadline on update preserves it. Downgrade retains
backfilled values and refuses to drop the new deadline column while it contains
data. Missing owners and overlength legacy values in narrowed fields must be
resolved before upgrading.

Before migrating an existing database, confirm the deployment history and
inspect the schema. If an earlier draft of `ef72b89db261` was already applied,
Alembic will see the same revision ID. A forward reconciliation revision
must be designed against that database's actual schema and data provenance.
For populated databases, rehearse the upgrade and schedule a low-traffic
window. The revision holds exclusive locks on users and tasks until commit.

## Verification

With test-only `DATABASE_URL` and `SECRET_KEY` configured:

```sh
python -m pip check
python -m pytest -m "not postgresql"
python -m pytest -m postgresql
```

The first suite uses in-memory SQLite and ORM metadata. The second requires
`POSTGRES_TEST_DATABASE_URL` pointing to a **disposable PostgreSQL database**
whose test user can create and drop schemas. It creates a fresh schema and
runs Alembic before executing API requests. CI runs both suites on PostgreSQL
14 and 15 with Python 3.11. Direct dependencies are pinned in
`requirements.txt`. Transitive dependencies are resolved at install time.

The image build context denies files by default. When adding runtime modules
or migrations, update `.dockerignore`. The CI image job checks application
files, tests exclusion with harmless sentinels, and smoke-tests Compose.

## License

[MIT](LICENSE)
