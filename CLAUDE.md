# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FastAPI REST API for currencies and exchange rates (no web UI), built to the
[zhukovsd CurrencyExchange spec](https://zhukovsd.github.io/python-backend-learning-course/projects/currency-exchange/).
Synchronous SQLAlchemy 2.0 over SQLite, Alembic migrations, pytest + factory_boy. The spec asks for plain `http.server` + `sqlite3`; FastAPI is a deliberate choice (see README). Everything else should follow the spec.

## Commands

Pinned deps (2024) need Python 3.11–3.12; `pydantic_core==2.16.3` has no wheels for 3.14.

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv -r requirements.txt
python -m playwright install chromium   # for e2e; or reuse an installed browser, see below
pre-commit install
cp .env.example .env                    # only for running the app; tests set their env in pytest.ini

make run-dev                      # python run.py (uvicorn, reload=True)
make run-prod                     # alembic upgrade head, then run.py
make frontend                     # spec's reference frontend on :8080 -> API on :8000
make lint                         # ruff check + ruff format on src, tests, e2e
make test                         # unit/integration tests (tests/ only)
make test-cov                     # same + coverage (fails under 80%), HTML in tests/coverage/
make test-e2e                     # browser tests in e2e/

pytest tests/exchange/test_routes.py::test_exchange_currency_direct   # single test
alembic revision --autogenerate -m "msg"                              # new migration
```

On this Windows machine Playwright can't download Chromium (TLS interception), so run e2e on the installed Edge: `make test-e2e E2E_ARGS="--browser-channel msedge"`. CI uses the downloaded Chromium.

CI (`.github/workflows/ci.yml`) runs three jobs on every PR: pre-commit (hygiene hooks + ruff), `make test-cov` and `make test-e2e`.

## Tests

- `tests/` — integration tests through `TestClient`. `pytest.ini` (via pytest-env) points them at `./test.db`. The session `db` fixture drops and recreates all tables, and `app_client` deletes all rows before each test. Factories (`tests/factories.py`) commit on creation. Seed data with the `create_currency_*` / `create_exc_rate_*` fixtures.
- `e2e/` — Playwright tests that drive the spec's reference frontend ([zhukovsd/currency-exchange-frontend](https://github.com/zhukovsd/currency-exchange-frontend), pinned by `FRONTEND_COMMIT` in `e2e/frontend.py`). It is fetched into the gitignored `e2e/frontend/` as a shallow download of only that commit, and only when it's missing, so bumping the pin needs no manual cleanup. Local edits in `e2e/frontend/` are overwritten. `e2e/conftest.py` migrates a temp SQLite DB, starts uvicorn on a free port with CORS for the frontend origin, and serves the frontend from a thread. The frontend's hardcoded API root in `js/app.js` is rewritten on the fly, never patched on disk. Each test starts with empty tables. Seed data through the `api` fixture (httpx), not the UI.
- The frontend reads `error.message` from every error response and shows it in `#api-error-toast`. That is why the error format matters beyond the unit tests.

## Known spec violations (open)

Each of these has a `xfail(strict=True)` e2e test in `e2e/test_frontend.py` (`BUG_*` markers). A fix must remove its marker: strict xfail fails the run once the bug is gone.

- A duplicate exchange rate pair returns 409 with the text "Server error" (`BUG_DUPLICATE_RATE_MESSAGE`). Base `AlreadyExists` has no `DETAIL`, and the exchange rate router doesn't map it the way the currency router does.
- The cross rate through USD is computed as (USD→A) / (USD→B), but it should be (USD→B) / (USD→A) (`BUG_CROSS_RATE`). The unit test `test_exchange_currency_rate_through_usd` pins the wrong value 0.72.

Not covered by e2e yet:
- PATCH on a missing pair returns 500 instead of 404.
- Routes have a trailing slash (`/currencies/`), so the spec paths answer with a 307 redirect (the browser follows it).
- Money goes through `float` in the conversion math, and rates are rounded with `math.ceil`. `amount` is already parsed as `Decimal`.

## Architecture

Each domain package (`src/currency`, `src/exchange_rate`, `src/exchange`) has `router.py` → `service.py`, plus `schemas.py` and `exceptions.py`. Shared pieces live at the top of `src/`:

- `database.py` — one module-level engine (`StaticPool`, `echo=True`). Services don't use FastAPI DI for sessions. They build `select()` statements and call `fetch_one` / `fetch_all` / `upd_one`, which each open and close their own session. `upd_one` turns `IntegrityError` into `AlreadyExists` (409).
- `models.py` — all ORM models in one file (`Currency`, `ExchangeRates`). `ExchangeRates` eagerly joins both currencies. Constraint names come from `constants.DB_NAMING_CONVENTION`. Alembic's `env.py` uses `src.models.Base.metadata` and `src.database.engine`.
- `exceptions.py` — `DetailedHTTPException` subclasses set `STATUS_CODE`/`DETAIL` as class attributes. Domain exceptions subclass these (e.g. `CurrencyNotFound(NotFound)`) and are raised directly from services. `register_exception_handlers` (called in `main.py`) renders every `HTTPException`, including Starlette's own 404/405, as `{"message": detail}`, and any unhandled exception as `500 {"message": "Server error"}`. It also turns validation errors into `400 {"message": "Missing required field 'x'"}` / `"Invalid field 'x': ..."`. That covers FastAPI's `RequestValidationError` and the plain pydantic `ValidationError` raised when `as_form` builds a schema. Never return `{"detail": ...}`: the spec and the frontend read `message`.
- `settings.py` — `AppSettings` (`APP_` prefix) and `ServerSettings` (`SERVER_` prefix), created once at import as `settings.app` / `settings.server`. `APP_CORS_ORIGINS` and `APP_CORS_HEADERS` are required.

Conventions to keep:

- **Form input, not JSON.** POST/PATCH bodies are form fields. Each schema has an `as_form` classmethod used as `Depends(Schema.as_form)`, and that is where camelCase form names (`baseCurrencyCode`) are mapped to snake_case fields.
- **camelCase responses** come from Pydantic `alias` + `AliasChoices`. `rate` is a `Decimal` that is serialized to float in JSON.
- **Currency pair codes** like `USDEUR` are split by `utils.parse_currency_pair` (first 3 chars / rest). `exchange_rate.service.get_exc_rate` filters through `joinedload(...).and_(...)` with `innerjoin`, not through a `WHERE` clause.
- **Conversion** (`exchange.service.get_rate`) tries, in order: the direct rate A→B, the inverse of B→A, then a cross rate through USD. Rates are rounded to 6 decimals and amounts to 2.
- **Validate input on the request side**: `Query(gt=0)` and the `as_form` schemas. Response DTOs (`exchange.schemas.Exchange`) carry no `ge`/`decimal_places`, because a constraint on a response schema turns bad input into a 500. Parse numeric query params as `Decimal`, not `float`: with `float`, FastAPI 0.110 lets `inf` through even with `allow_inf_nan=False`.
- Empty-code routes (`/currency/`, `/exchangeRate/`) exist only to return a 400 and are hidden from the schema.
