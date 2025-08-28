# library-api
Library inventory API

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
