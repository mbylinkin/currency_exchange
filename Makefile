# Extra pytest-playwright args, e.g. E2E_ARGS="--browser-channel msedge --headed"
E2E_ARGS ?=

# Create/update .venv from uv.lock (app + dev dependencies)
install:
	uv sync


# Apply migrations; creates the SQLite file and tables on first run
migrate:
	uv run alembic upgrade head


# Fail if models.py has schema changes that no migration covers.
# Runs on a throwaway DB, so it needs no .env.
check-migrations: export APP_DATABASE_URL = sqlite:///./.migrations-check.db
check-migrations: export APP_CORS_ORIGINS = []
check-migrations: export APP_CORS_HEADERS = []
check-migrations:
	rm -f .migrations-check.db
	uv run alembic upgrade head
	uv run alembic check
	rm -f .migrations-check.db


run-dev: export APP_DEBUG = true
run-dev: migrate
	uv run python run.py


# No reload, no SQL log, unless APP_DEBUG=true is set in .env
run-prod: migrate
	uv run python run.py


# Reference frontend from the spec on :8080, talking to the API on :8000
frontend:
	uv run python e2e/frontend.py --port 8080 --api-url http://localhost:8000


# API on :8000 + reference frontend on :8080 in containers (DB in a volume)
docker-up:
	docker compose up --build --detach --wait


docker-down:
	docker compose down


lint:
	uv run ruff check .
	uv run ruff format .


# mypy --strict on src and e2e, relaxed for tests (config in pyproject.toml)
typecheck:
	uv run mypy


test:
	uv run pytest tests


test-cov:
	uv run pytest tests -v --cov=src --cov-report=html --cov-report=term


test-e2e:
	uv run pytest e2e $(E2E_ARGS)
