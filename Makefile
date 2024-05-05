run-dev:
	python run.py


run-prod:
	alembic upgrade head
	python run.py


lint:
	ruff check src
	ruff format src
	ruff check tests
	ruff format tests


test:
	pytest .


test-cov:
	pytest -v --cov=. --cov-report=html
