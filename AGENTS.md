# AGENTS.md

## Project rules

This is a production-oriented FastAPI technical assignment.

Hard constraints:

- Use Python and FastAPI.
- Use async/await where appropriate.
- Use FastAPI Depends for dependency injection.
- Use Pydantic models.
- Use exception handlers.
- Use FastAPI lifespan for startup and shutdown.
- Use PostgreSQL with asyncpg.
- Do not use any ORM.
- Do not use SQLite.
- Do not create files over 500 lines.
- Prefer files under 250 lines.
- Keep architecture simple: router, schemas, service, repository, email client, db pool.
- Treat email sending as a third-party service abstraction.
- Use a fake email provider that prints/logs the 4-digit activation code.
- The app must run with Docker Compose.
- Tests must run with Docker Compose.
- Do not add Redis, Celery, Kafka, Kubernetes, frontend, JWT, or unnecessary infrastructure.
- Do not commit secrets.

## Test commands

Use:
docker compose run --rm api pytest

## Development style

Make small, focused changes.
Do not rewrite unrelated files.
Keep commits logically separated.
