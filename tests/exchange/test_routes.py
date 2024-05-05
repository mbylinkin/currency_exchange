from fastapi.testclient import TestClient
from fastapi import status

from src import models


def test_exchange_currency_direct(
    app_client: TestClient, create_exc_rate_usd_eur: models.ExchangeRates
) -> None:
    resp = app_client.get(
        "/exchange/", params={"from": "USD", "to": "EUR", "amount": 1.0}
    )

    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert resp_json["amount"] == 1.0
    assert resp_json["convertedAmount"] == 1.1


def test_exchange_currency_reversed(
    app_client: TestClient, create_exc_rate_usd_eur: models.ExchangeRates
) -> None:
    resp = app_client.get(
        "/exchange/", params={"from": "EUR", "to": "USD", "amount": 1.0}
    )

    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert resp_json["amount"] == 1.0
    assert resp_json["convertedAmount"] == 0.91


def test_exchange_currency_rate_through_usd(
    app_client: TestClient, create_exc_rate_list: list[models.ExchangeRates]
) -> None:
    resp = app_client.get(
        "/exchange/", params={"from": "EUR", "to": "GBP", "amount": 1.0}
    )

    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert resp_json["amount"] == 1.0
    assert resp_json["convertedAmount"] == 0.72


def test_exchange_currency_rate_not_found(
    app_client: TestClient, create_currency_eur, create_currency_gpb
) -> None:
    resp = app_client.get(
        "/exchange/", params={"from": "EUR", "to": "GBP", "amount": 1.0}
    )

    resp_json = resp.json()

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp_json["detail"] == "Exchange rate for currency pair not found"


def test_exchange_currency_not_found(
    app_client: TestClient, create_currency_eur, create_currency_gpb
) -> None:
    resp = app_client.get(
        "/exchange/", params={"from": "EUR", "to": "GBP", "amount": 1.0}
    )

    resp_json = resp.json()

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp_json["detail"] == "Exchange rate for currency pair not found"
