# "Currency exchange" web application using FastAPI

REST API for describing currencies and exchange rates. It allows users to view and edit lists of currencies and exchange rates, perform conversion calculations for arbitrary amounts from one currency to another.

The implementation does not include a web interface.

[Project specification](https://zhukovsd.github.io/python-backend-learning-course/Projects/CurrencyExchange/)

## Motivation
* Learn MVC Pattern [(docs)](https://gist.github.com/SergeyCP/0fd7f5ef83c48acc723de821315e01e9)
* Learn REST API
* Use FastAPI to build a REST API following [fastapi best practicies](https://github.com/zhanymkanov/fastapi-best-practices#3-use-dependencies-for-data-validation-vs-db) and [fastapi production template](https://github1s.com/zhanymkanov/fastapi_production_template/blob/main/src/config.py)
* Use SQLAlchemy to create database and tables for storing data [(SQLAlchemy course)](https://www.youtube.com/playlist?list=PLeLN0qH0-mCXARD_K-USF2wHctxzEVp40)
* Use [alembic](https://alembic.sqlalchemy.org/) for managing migrations
* Use [pytest](https://docs.pytest.org/) and [Factory Boy](https://factoryboy.readthedocs.io/) for testing


## Getting started

### Create environment variables

```bash
cp .env.example .env
```
Creates .env file from .env.example

### Install dependencies

Requires [uv](https://docs.astral.sh/uv/). uv installs Python 3.14 itself if it's missing.

```bash
make install    # or: uv sync
```
Creates `.venv` with the app and dev dependencies, pinned in `uv.lock`. Use `uv add <pkg>` (or `uv add --dev <pkg>`) to add a dependency. All `make` targets run through `uv run`, so there is no need to activate the venv.

### Run server

```bash
make run-dev
```
This command (`make run-prod` does the same):
* creates database if it doesn't exist
* applies migrations (`make migrate`), so tables are created or updated
* starts web application server

### Use application

* Server available at http://127.0.0.1:8000
* REST API docs available at http://localhost:8000/docs#/


## Tests

All tests are integrational.

To run tests use
```bash
make test
```

To run tests with coverage use
```bash
make test-cov
```
After running tests with coverage report will be available at [tests/coverage/index.html](tests/coverage/index.html)

### End-to-end tests

E2E tests drive the [reference frontend](https://github.com/zhukovsd/currency-exchange-frontend) from the spec in a browser (Playwright). They start the API and the frontend themselves, no `.env` needed.

```bash
uv run playwright install chromium
make test-e2e
```

To use an already installed browser instead of the downloaded Chromium, run `make test-e2e E2E_ARGS="--browser-channel msedge"` (or `chrome`). Add `--headed` to watch the browser.

To click through the frontend by hand, start the API (`make run-dev`) and then the frontend (`make frontend`), and open http://localhost:8080.

### Pre-commit hooks

```bash
uv run pre-commit install
```

Runs whitespace/YAML checks and ruff (lint + format) on every commit. CI runs the same hooks plus the unit and e2e tests on every pull request.
