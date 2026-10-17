import pytest
from fastapi import status
from fastapi.testclient import TestClient

from src.main import app


def test_unknown_route_uses_message_format(app_client: TestClient) -> None:
    resp = app_client.get("/unknown")

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json() == {"message": "Not Found"}


def test_unhandled_error_returns_500_message(
    cleanup_db: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    def broken() -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr("src.currency.router.get_currency_list", broken)
    client = TestClient(app, raise_server_exceptions=False)

    resp = client.get("/currencies")

    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert resp.json() == {"message": "Server error"}


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/currencies"),
        ("POST", "/currencies"),
        ("GET", "/exchangeRates"),
        ("POST", "/exchangeRates"),
        ("GET", "/exchange?from=USD&to=EUR&amount=1"),
    ],
)
def test_spec_paths_are_not_redirected(
    app_client: TestClient, method: str, path: str
) -> None:
    resp = app_client.request(method, path, follow_redirects=False)

    assert not resp.is_redirect, resp.headers.get("location")
