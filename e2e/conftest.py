import json
import os
import socket
import sqlite3
import subprocess
import sys
import threading
import time
from collections.abc import Generator
from pathlib import Path

import httpx2
import pytest
from playwright.sync_api import Page

from .frontend import fetch_frontend, make_server

ROOT_DIR = Path(__file__).parent.parent


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port: int = sock.getsockname()[1]
        return port


@pytest.fixture(scope="session")
def frontend_port() -> int:
    return free_port()


@pytest.fixture(scope="session")
def frontend_url(frontend_port: int) -> str:
    # Must match the CORS origin the backend allows
    return f"http://localhost:{frontend_port}"


@pytest.fixture(scope="session")
def db_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("e2e") / "e2e.db"


@pytest.fixture(scope="session")
def backend_url(db_path: Path, frontend_url: str) -> Generator[str]:
    port = free_port()
    env = {
        **os.environ,
        "APP_ENVIRONMENT": "TESTING",
        "APP_DATABASE_URL": f"sqlite:///{db_path.as_posix()}",
        "APP_CORS_ORIGINS": json.dumps([frontend_url]),
        "APP_CORS_HEADERS": json.dumps(["*"]),
    }
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT_DIR,
        env=env,
        check=True,
        capture_output=True,
    )
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.main:app", "--port", str(port)],
        cwd=ROOT_DIR,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://localhost:{port}"
    try:
        for _ in range(50):
            try:
                httpx2.get(f"{url}/healthcheck")
                break
            except httpx2.TransportError:
                time.sleep(0.2)
        else:
            raise RuntimeError("Backend did not start")
        yield url
    finally:
        server.terminate()
        server.wait()


@pytest.fixture(scope="session")
def frontend(frontend_port: int, frontend_url: str, backend_url: str) -> Generator[str]:
    fetch_frontend()
    server = make_server(frontend_port, backend_url)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield frontend_url
    server.shutdown()


@pytest.fixture(autouse=True)
def clean_db(backend_url: str, db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM exchange_rates")
        conn.execute("DELETE FROM currency")


@pytest.fixture()
def api(backend_url: str) -> Generator[httpx2.Client]:
    # Seeds data directly through the API, bypassing the UI under test
    with httpx2.Client(base_url=backend_url) as client:
        yield client


@pytest.fixture()
def page_errors(page: Page) -> list[str]:
    errors: list[str] = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    return errors
