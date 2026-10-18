# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FastAPI REST API for currencies and exchange rates (no web UI), built to the
[zhukovsd CurrencyExchange spec](https://zhukovsd.github.io/python-backend-learning-course/projects/currency-exchange/).
Synchronous SQLAlchemy 2.1 over SQLite, Alembic migrations, pytest + factory_boy. The spec asks for plain `http.server` + `sqlite3`; FastAPI is a deliberate choice (see README). Everything else should follow the spec.

## Commands

The project is managed with [uv](https://docs.astral.sh/uv/). The Python version (3.14) comes from `.python-version`. `pyproject.toml` holds the dependencies and the pytest, pytest-env, coverage and ruff config. App dependencies live in `[project]`, everything for development in `[dependency-groups].dev`. `uv.lock` is generated: never edit it by hand. CI runs `uv sync --locked`, which fails if the lock is stale.

```bash
uv add <pkg>                  # app dependency
uv add --dev <pkg>            # dev/test dependency
uv lock --upgrade             # bump everything (then run tests + e2e)
uv lock --upgrade-package <pkg>
```

Ruff's target version comes from `requires-python`. FastAPI's `Depends`/`Query`/`Form` defaults are whitelisted for bugbear B008 in `[tool.ruff.lint.flake8-bugbear]`. `alembic` is declared `known-third-party` for isort, because the local `alembic/` directory would otherwise make it first-party. After bumping ruff, set the same version as `rev` of `ruff-pre-commit` in `.pre-commit-config.yaml` (`pre-commit autoupdate` does it).

Dependabot (`.github/dependabot.yml`) opens weekly PRs for `uv.lock` and for GitHub Actions. Minor and patch bumps come grouped into one PR, each major bump gets its own. Dependabot doesn't update `.pre-commit-config.yaml`, so when its PR bumps ruff, push `pre-commit autoupdate` onto the same branch.

```bash
make install                            # uv sync: .venv with app + dev deps
uv run playwright install chromium      # for e2e; or reuse an installed browser, see below
uv run pre-commit install
cp .env.example .env                    # only for running the app; tests set their env via [tool.pytest_env]

make migrate                      # alembic upgrade head (also run by run-dev/run-prod)
make check-migrations             # fails if models.py changed without a migration (CI runs it)
make run-dev                      # migrate, then python run.py with APP_DEBUG=true: uvicorn reload + SQL log
make run-prod                     # same without reload and SQL log (APP_DEBUG from .env, default false)
make frontend                     # spec's reference frontend on :8080 -> API on :8000
make lint                         # ruff check + ruff format on the whole repo (alembic/ and run.py included)
make typecheck                    # mypy: strict everywhere, relaxed for tests/ (CI runs it)
make test                         # unit/integration tests (tests/ only)
make test-cov                     # same + coverage (fails under 80%), HTML in tests/coverage/
make test-e2e                     # browser tests in e2e/

uv run pytest tests/exchange/test_routes.py::test_exchange_currency_direct   # single test
uv run alembic revision --autogenerate -m "msg"                              # new migration after changing models.py (post-write hooks in alembic.ini run ruff on it)
```

On this Windows machine Playwright can't download Chromium (TLS interception), so run e2e on the installed Edge: `make test-e2e E2E_ARGS="--browser-channel msedge"`. CI uses the downloaded Chromium.

CI (`.github/workflows/ci.yml`) runs three jobs on every PR: pre-commit (hygiene hooks + ruff), `make typecheck` + `make check-migrations` + `make test-cov`, and `make test-e2e`. Alembic's `env.py` imports app settings, so any alembic command needs `APP_CORS_ORIGINS`/`APP_CORS_HEADERS` set: from `.env` locally, from the Makefile target in CI.

## Tests

- `tests/` — integration tests through `TestClient`. `[tool.pytest_env]` in `pyproject.toml` points them at `./test.db`. The session `db` fixture drops and recreates all tables, and `app_client` deletes all rows before each test. Factories (`tests/factories.py`) commit on creation. Seed data with the `create_currency_*` / `create_exc_rate_*` fixtures.
- `e2e/` — Playwright tests that drive the spec's reference frontend ([zhukovsd/currency-exchange-frontend](https://github.com/zhukovsd/currency-exchange-frontend), pinned by `FRONTEND_COMMIT` in `e2e/frontend.py`). It is fetched into the gitignored `e2e/frontend/` as a shallow download of only that commit, and only when it's missing, so bumping the pin needs no manual cleanup. Local edits in `e2e/frontend/` are overwritten. `e2e/conftest.py` migrates a temp SQLite DB, starts uvicorn on a free port with CORS for the frontend origin, and serves the frontend from a thread. The frontend's hardcoded API root in `js/app.js` is rewritten on the fly, never patched on disk. Each test starts with empty tables. Seed data through the `api` fixture (httpx), not the UI.
- The frontend reads `error.message` from every error response and shows it in `#api-error-toast`. That is why the error format matters beyond the unit tests.

## Spec violations

None known. Fix them one per branch/PR, red test first.

To pin a bug that is visible through the frontend before fixing it, add a named constant to `e2e/test_frontend.py`: `BUG_X = pytest.mark.xfail(strict=True, reason=...)`. The fix deletes the constant and its usages. Strict xfail fails the run once the bug is gone.

## Architecture

Each domain package (`src/currency`, `src/exchange_rate`, `src/exchange`) has `router.py` → `service.py`, plus `schemas.py` and `exceptions.py`. Shared pieces live at the top of `src/`:

- `database.py` — one module-level engine (`StaticPool`, `echo=settings.app.debug`). Services don't use FastAPI DI for sessions. They build `select()` statements and call `fetch_one` / `fetch_all` / `upd_one`, which each open and close their own session. `upd_one` turns `IntegrityError` into `AlreadyExists` (409).
- `models.py` — all ORM models in one file (`Currency`, `ExchangeRates`). `ExchangeRates` eagerly joins both currencies. Constraint names come from `constants.DB_NAMING_CONVENTION`. Alembic's `env.py` uses `src.models.Base.metadata` and `src.database.engine`. Declare columns as typed `Mapped[...] = mapped_column(...)`, never bare `sa.Column`. `Mapped[X]` means NOT NULL and `Mapped[X | None]` means nullable, so the type annotation is the schema. Alembic runs in batch mode (`render_as_batch=True`), because SQLite can't `ALTER COLUMN`. Check the autogenerated `batch_alter_table` migrations and test them on a DB that has data.
- `exceptions.py` — `DetailedHTTPException` subclasses set `STATUS_CODE`/`DETAIL` as class attributes. Domain exceptions subclass these (e.g. `CurrencyNotFound(NotFound)`) and are raised directly from services. Services expose `get_x` (may return `None`) and `get_valid_x` (raises 404). Use `get_valid_x` wherever a missing record is a client error. Routers map the generic `AlreadyExists` that `upd_one` raises to a domain-specific 409 (`CurrencyAlreadyExists`, `ExcRateAlreadyExists`). `register_exception_handlers` (called in `main.py`) renders every `HTTPException`, including Starlette's own 404/405, as `{"message": detail}`, and any unhandled exception as `500 {"message": "Server error"}`. It also turns validation errors into `400 {"message": "Missing required field 'x'"}` / `"Invalid field 'x': ..."`. That covers FastAPI's `RequestValidationError` and the plain pydantic `ValidationError` raised when `as_form` builds a schema. Never return `{"detail": ...}`: the spec and the frontend read `message`.
- `settings.py` — `AppSettings` (`APP_` prefix; `APP_DEBUG` turns on uvicorn reload and SQL logging, `APP_ENVIRONMENT` controls docs and `root_path`) and `ServerSettings` (`SERVER_` prefix), created once at import as `settings.app` / `settings.server`. `APP_CORS_ORIGINS` and `APP_CORS_HEADERS` are required.

Conventions to keep:

- **Form input, not JSON.** POST/PATCH bodies are form fields. Each schema has an `as_form` classmethod used as `Depends(Schema.as_form)`, and that is where camelCase form names (`baseCurrencyCode`) are mapped to snake_case fields.
- **camelCase responses** come from Pydantic `alias` + `AliasChoices`. `rate` is a `Decimal` that is serialized to float in JSON.
- **Currency codes are case-insensitive.** `CurrencyCreate` stores them uppercase, and `currency.service.get_currency` / `exchange_rate.service.get_exc_rate` uppercase the code before the lookup, so `usd`, `usdEur` and `/exchange?from=usd` resolve. Every other lookup goes through these two functions.
- **Currency pair codes** like `USDEUR` are split by `utils.parse_currency_pair` (first 3 chars / rest). `exchange_rate.service.get_exc_rate` filters through `joinedload(...).and_(...)` with `innerjoin`, not through a `WHERE` clause.
- **Conversion** (`exchange.service.get_rate`) tries, in order: the direct rate A→B, the inverse of B→A, then a cross rate through USD computed as (USD→B) / (USD→A). Computed rates are rounded to 6 decimals and converted amounts to 2, both `ROUND_HALF_UP` via `utils.round_rate` / `round_amount`.
- **Money is `Decimal` end to end**: query param → DB → math. It becomes a float only in the JSON serializers, after rounding. Never build a `Decimal` from a `float`. Don't use `round()` on money either, because for `Decimal` it is banker's rounding.
- **Validate input on the request side**: `Query(gt=0)` and the `as_form` schemas. Response DTOs (`exchange.schemas.Exchange`) carry no `ge`/`decimal_places`, because a constraint on a response schema turns bad input into a 500. Parse numeric query params as `Decimal`, not `float`: with `float`, FastAPI 0.110 lets `inf` through even with `allow_inf_nan=False`.
- **Route paths match the spec exactly, with no trailing slash** (`/currencies`, `/exchangeRates`, `/exchange`). A trailing slash makes the spec path answer with a 307 redirect. `test_spec_paths_are_not_redirected` and the e2e `test_frontend_requests_are_not_redirected` guard this.
- Empty-code routes (`/currency/`, `/exchangeRate/`) exist only to return a 400 and are hidden from the schema.
