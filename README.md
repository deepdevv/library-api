# library-api
Library inventory API

## Overview

Simple Library API used by staff to track books:

- Each book: ```serial_number``` (six-digit string), ```title```, ```author```, ```is_borrowed```, ```borrowed_at```, ```borrower_card``` (six-digit string).

- API supports: **add**, **delete**, **list**, **update borrow status (borrow/return)**.

- No auth.

- Stack: FastAPI + SQLAlchemy 2.x (async) + PostgreSQL + Alembic. Docker Compose provided.

## Quick start (Docker)
```bash
# 1) Copy env template and adjust if needed
cp .env.example .env

# 2) Start DB + API (migrations run automatically)
docker compose up --build

# API: http://localhost:8000  |  Docs: http://localhost:8000/docs
```

## Run locally (no Docker)
```bash
# Ensure Postgres running at localhost:55432 (docker compose up -d db)
uvicorn app.main:app --reload
```

# API endpoints (v1)

Base path: `/api/v1`

| Method | Path                           | Body (JSON)                                                                 | Success                              | Errors (examples)                          |
|--------|--------------------------------|------------------------------------------------------------------------------|---------------------------------------|--------------------------------------------|
| POST   | `/books`                       | `{serial_number, title, author}`                                            | `201 BookRead` + `Location`           | 409 conflict (duplicate), 422 validation    |
| DELETE | `/books/{serial_number}`       | —                                                                            | `204`                                 | 404 not found, 409 if borrowed              |
| GET    | `/books`                       | — (query: `is_borrowed`, `author`, `title`, `limit`, `offset`)              | `200 {items, total}`                  | —                                          |
| PATCH  | `/books/{serial_number}/status`| Borrow: `{"action":"borrow","borrower_card":"123456"}` <br> Return: `{"action":"return"}` | `200 BookRead`                        | 404 not found, 409 invalid state, 422 validation |

## Error envelope
```
{ "error": { "code": "conflict|not_found|validation_error", "message": "...", "details": {} } }
```

### Acceptance checklist (mapped to the brief)

 - Add new book (POST /books).

 - Delete book (DELETE /books/{serial_number}); blocked if borrowed.

 - List books (GET /books) with filters and pagination.

 - Update status: borrow/return (PATCH /books/{serial_number}/status).

 - Six-digit constraints for serial_number and borrower_card; borrow consistency enforced at DB and service layers.

 - One-command start: docker compose up → DB + API + migrations.

 - PostgreSQL used as DB.

## Testing

This project uses **pytest** with async support and coverage reporting.

### Strategy

- **Unit tests**

  - Pydantic schemas (validation, discriminated unions).

  - Service layer (business rules, conflict handling).

- **Integration tests**

  - Repository layer against a transactional DB.

  - API endpoints with FastAPI ```AsyncClient``` and dependency overrides.

- **Contract tests**

  - Error envelope shape (```{ "error": { "code", "message", "details" } }```).

  - OpenAPI schema presence and examples.

### Running tests

All tests are async-friendly and run in an isolated PostgreSQL schema (via fixtures).

```
pytest
```

### Coverage

Coverage is measured automatically with ```pytest-cov```.
Minimum threshold is enforced (85%):
```
pytest --cov=app --cov-report=term-missing
```

- ```--cov=app``` → measure only project code

- ```--cov-report=term-missing``` → show untested lines

- ```--cov-fail-under=85``` → fail build if coverage drops below 85%

### Adding new tests

- Place new test modules under ```tests/```.

- Use ```pytest.mark.asyncio``` for async tests.

- Reuse fixtures (```db_session```, ```client```) for DB/API access.

