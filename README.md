# "Currency exchange" web application using FastAPI

REST API for describing currencies and exchange rates. It allows users to view and edit lists of currencies and exchange rates, perform conversion calculations for arbitrary amounts from one currency to another.

The implementation does not include a web interface. The spec's [reference frontend](https://github.com/zhukovsd/currency-exchange-frontend) works with it (see [Docker](#docker) and [End-to-end tests](#end-to-end-tests)).

[Project specification](https://zhukovsd.github.io/python-backend-learning-course/projects/currency-exchange/)

### Why FastAPI

The spec asks for plain `http.server` and `sqlite3`, without frameworks. This project uses FastAPI and SQLAlchemy on purpose, to practice using them. Everything else follows the spec: routes, status codes, form input, the response format and the conversion rules.

## Motivation
* Learn MVC Pattern
* Learn REST API
* Use FastAPI to build a REST API following [fastapi best practices](https://github.com/zhanymkanov/fastapi-best-practices#dependencies) and [fastapi production template](https://github.com/zhanymkanov/fastapi_production_template/blob/main/src/config.py)
* Use SQLAlchemy to create database and tables for storing data [(SQLAlchemy course)](https://www.youtube.com/playlist?list=PLeLN0qH0-mCXARD_K-USF2wHctxzEVp40)
* Use [alembic](https://alembic.sqlalchemy.org/) for managing migrations
* Use [pytest](https://docs.pytest.org/) and [Factory Boy](https://factoryboy.readthedocs.io/) for testing

## API

| Method | Path | Description |
|---|---|---|
| GET | `/currencies` | List of currencies |
| GET | `/currency/{code}` | One currency, e.g. `/currency/EUR` |
| POST | `/currencies` | Add a currency. Form fields: `name`, `code`, `sign` |
| GET | `/exchangeRates` | List of exchange rates |
| GET | `/exchangeRate/{pair}` | One rate, e.g. `/exchangeRate/USDEUR` |
| POST | `/exchangeRates` | Add a rate. Form fields: `baseCurrencyCode`, `targetCurrencyCode`, `rate` |
| PATCH | `/exchangeRate/{pair}` | Update a rate. Form field: `rate` |
| GET | `/exchange?from=USD&to=EUR&amount=10` | Convert an amount |

* Request bodies are form fields (`application/x-www-form-urlencoded`), not JSON.
* Currency codes are case-insensitive: `usd`, `/exchangeRate/usdEur` and `/exchange?from=usd` all work.
* `/exchange` uses the direct rate A→B if it exists, otherwise the inverse of B→A, otherwise the cross rate through USD.
* Every error is `{"message": "..."}` with the status code from the spec: 400 for a missing or invalid field, 404 when nothing is found, 409 for a duplicate, 500 for a server error.

Interactive docs (Swagger UI) are at http://localhost:8000/docs, but only when `APP_ENVIRONMENT` is `LOCAL`, `TESTING` or `STAGING`. `.env.example` sets `LOCAL`. The default is `PRODUCTION`, which hides the docs, and the Docker image uses the default.

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
This command:
* creates database if it doesn't exist
* applies migrations (`make migrate`), so tables are created or updated
* starts web application server with `APP_DEBUG=true`: it reloads on code changes and logs every SQL query to the console

`make run-prod` does the same without reload and SQL log (unless `APP_DEBUG=true` is set in `.env`).

### Use application

* Server available at http://127.0.0.1:8000
* To click through the reference frontend, run `make frontend` in another terminal and open http://localhost:8080

## Docker

Requires Docker with Compose. No `.env` and no uv needed.

```bash
make docker-up      # docker compose up --build --detach --wait
make docker-down    # stop and remove the containers
```

* API: http://localhost:8000. Migrations are applied on start.
* Reference frontend: http://localhost:8080
* The SQLite database lives in the `data` volume, so it survives `docker-down`. `docker compose down -v` deletes it.

## Tests

All tests are integration tests: they call the API through FastAPI's `TestClient` and use a real SQLite database (`test.db`).

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

## Development

```bash
make lint               # ruff check + ruff format
make typecheck          # mypy (strict)
make check-migrations   # fails if models.py changed without a migration
uv run alembic revision --autogenerate -m "message"   # new migration after changing models.py
```

### Pre-commit hooks

```bash
uv run pre-commit install
```

Runs whitespace/YAML checks and ruff (lint + format) on every commit.

### CI

GitHub Actions run four jobs on every pull request:
* `lint`: the pre-commit hooks
* `test`: `make typecheck`, `make check-migrations`, `make test-cov`
* `e2e`: `make test-e2e`
* `docker`: builds the images, starts them with `docker compose`, adds a currency through the API and checks the frontend is served

Dependabot opens weekly pull requests for Python dependencies, Docker base images and GitHub Actions.
