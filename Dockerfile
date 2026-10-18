# API image (default target) and the spec's reference frontend (target "frontend").
# Both are run together by docker-compose.yml.

FROM ghcr.io/astral-sh/uv:0.13.1 AS uv


FROM python:3.14-slim AS builder
COPY --from=uv /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
# App dependencies only, exactly as pinned in uv.lock
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project


FROM python:3.14-slim AS frontend-fetch
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY e2e/frontend.py e2e/
RUN python e2e/frontend.py --fetch-only && rm -rf e2e/frontend/.git


FROM python:3.14-slim AS frontend
RUN useradd --create-home app
WORKDIR /app
COPY --from=frontend-fetch /app/e2e ./e2e
USER app
EXPOSE 8080
# The frontend was downloaded at build time. --api-url is the API as the
# browser sees it, so it stays on localhost even inside compose.
CMD ["python", "e2e/frontend.py", "--no-fetch", "--host", "0.0.0.0", "--port", "8080",      "--api-url", "http://localhost:8000"]


FROM python:3.14-slim AS api
RUN useradd --create-home app && mkdir /data && chown app /data
WORKDIR /app
COPY --from=builder /app/.venv ./.venv
COPY alembic.ini run.py ./
COPY alembic ./alembic
COPY src ./src
ENV PATH=/app/.venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    SERVER_HOST=0.0.0.0 \
    SERVER_PORT=8000 \
    APP_DATABASE_URL=sqlite:////data/currency_exchange.db \
    APP_CORS_ORIGINS='["http://localhost:8080"]' \
    APP_CORS_HEADERS='["*"]'
USER app
VOLUME /data
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthcheck')"]
CMD ["sh", "-c", "alembic upgrade head && exec python run.py"]
