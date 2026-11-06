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


# A migration that is already in origin/main may not be changed, renamed or
# deleted: databases have applied it. Fix forward with a new revision.
# Compares with the merge base, so uncommitted edits count too.
migrations-immutable:
	@changed=$$(git diff --name-only --diff-filter=DMR $$(git merge-base origin/main HEAD) -- alembic/versions/); 	if [ -n "$$changed" ]; then 		echo "Shipped migrations changed (add a new revision instead):"; echo "$$changed"; exit 1; 	fi; 	echo "Shipped migrations unchanged"


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


# Every check that CI runs, except e2e and the docker smoke test.
# Must pass before a change is done.
check: lint secrets vulns typecheck check-migrations migrations-immutable test-cov diff-cover


# All pre-commit hooks (hygiene + ruff) on the whole repo. Fails on any finding;
# hooks with an autofix also apply it, so run it again after reviewing the diff.
lint:
	uv run pre-commit run --all-files --show-diff-on-failure


# Committed secrets anywhere in git history (betterleaks). The commit hook
# only sees the staged diff, so this is the check that CI relies on.
secrets:
	uv run pre-commit run betterleaks-history --all-files --hook-stage manual


# Known vulnerabilities in uv.lock (osv-scanner, needs the network).
# Also runs weekly in CI: a new advisory can fail it without any change here.
vulns:
	uv run pre-commit run osv-scanner --all-files --hook-stage manual


# Regenerate openapi.json from the app; commit it with the API change
openapi:
	uv run python scripts/openapi.py


# Safe autofixes only
fix:
	uv run ruff check --fix .
	uv run ruff format .
	uv run rumdl fmt .


# mypy --strict on src and e2e, relaxed for tests (config in pyproject.toml)
typecheck:
	uv run mypy


test:
	uv run pytest tests


test-cov:
	uv run pytest tests -v --cov=src --cov-report=html --cov-report=term --cov-report=xml


# Lines this branch changes in src/ (vs origin/main) must be covered by tests.
# Reads coverage.xml from test-cov; the 80% total floor stays in pyproject.toml.
diff-cover:
	uv run diff-cover coverage.xml --compare-branch=origin/main --fail-under=90


test-e2e:
	uv run pytest e2e $(E2E_ARGS)
