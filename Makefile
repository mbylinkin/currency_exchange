# Extra pytest-playwright args, e.g. E2E_ARGS="--browser-channel msedge --headed"
E2E_ARGS ?=

run-dev:
	python run.py


run-prod:
	alembic upgrade head
	python run.py


# Reference frontend from the spec on :8080, talking to the API on :8000
frontend:
	python e2e/frontend.py --port 8080 --api-url http://localhost:8000


lint:
	ruff check src tests e2e
	ruff format src tests e2e


test:
	pytest tests


test-cov:
	pytest tests -v --cov=src --cov-report=html --cov-report=term


test-e2e:
	pytest e2e $(E2E_ARGS)
