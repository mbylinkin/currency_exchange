import itertools
import string
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from fastapi import status
from fastapi.testclient import TestClient

from src.main import app

CODES = ["".join(c) for c in itertools.product(string.ascii_uppercase, repeat=3)][:100]


def post_currency(code: str) -> int:
    # A client per call: each request runs on its own thread, like under uvicorn
    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.post("/currencies", data={"code": code, "name": "x", "sign": "x"})
    return resp.status_code


def test_concurrent_writes(app_client: TestClient) -> None:
    # Every code is posted twice: one request creates it, the other gets 409
    with ThreadPoolExecutor(max_workers=32) as pool:
        statuses = Counter(pool.map(post_currency, CODES * 2))

    assert statuses == {
        status.HTTP_201_CREATED: len(CODES),
        status.HTTP_409_CONFLICT: len(CODES),
    }
    assert len(app_client.get("/currencies").json()) == len(CODES)
