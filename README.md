# library-api
**Library inventory API** built with **FastAPI** + **SQLAlchemy (async)** + **PostgreSQL**.

## Overview

Simple Library API used by staff to track books:

- Each book: ```serial_number``` (six-digit string), ```title```, ```author```, ```is_borrowed```, ```borrowed_at```, ```borrower_card``` (six-digit string).

- API supports: **add**, **delete**, **list**, **update borrow status (borrow/return)**.

- No auth.

- Stack: FastAPI + SQLAlchemy 2.x (async) + PostgreSQL + Alembic. Docker Compose provided.

## Quick start (Docker)
```bash
# 1) Copy env template
cp .env.example .env

# 2) Start DB + API (migrations run automatically)
docker compose up --build

# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```


## One-minute demo
```bash
# Add a book
http POST :8000/api/v1/books serial_number=123456 title="Clean Code" author="Robert C. Martin"
curl -X POST http://localhost:8000/api/v1/books \
  -H "Content-Type: application/json" \
  -d '{"serial_number":"123456","title":"Clean Code","author":"Robert C. Martin"}'

# Borrow it
http PATCH :8000/api/v1/books/123456/status action=borrow borrower_card=654321
curl -X PATCH http://localhost:8000/api/v1/books/123456/status \
  -H "Content-Type: application/json" \
  -d '{"action":"borrow","borrower_card":"654321"}'

# List borrowed books
http GET :8000/api/v1/books is_borrowed==true
curl "http://localhost:8000/api/v1/books?is_borrowed=true"

# Return it
http PATCH :8000/api/v1/books/123456/status action=return
curl -X PATCH http://localhost:8000/api/v1/books/123456/status \
  -H "Content-Type: application/json" \
  -d '{"action":"return"}'

http DELETE :8000/api/v1/books/123456
curl -X DELETE http://localhost:8000/api/v1/books/123456
```
## Environment variables
All required settings are already defined in ```.env.example```.
Just copy it to ```.env``` and you’re good to go — no edits needed for Docker Compose.

### Local override (optional)

If you want to run the API outside Docker (with Postgres on localhost), uncomment and adjust:
```bash
DATABASE_URL=postgresql+asyncpg://library:library@localhost:55432/library
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
```json
{
 "error": {
  "code": "conflict | not_found | validation_error",
  "message": "...",
  "details": {}
 }
}
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



