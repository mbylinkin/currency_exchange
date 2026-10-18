import pytest
from fastapi import status
from fastapi.testclient import TestClient

from src import models

from ..factories import ExchangeRateFactory


def test_exchange_currency_direct(
    app_client: TestClient, create_exc_rate_usd_eur: models.ExchangeRates
) -> None:
    resp = app_client.get(
        "/exchange", params={"from": "USD", "to": "EUR", "amount": 1.0}
    )

    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert resp_json["amount"] == 1.0
    assert resp_json["convertedAmount"] == 1.1


def test_exchange_currency_reversed(
    app_client: TestClient, create_exc_rate_usd_eur: models.ExchangeRates
) -> None:
    resp = app_client.get(
        "/exchange", params={"from": "EUR", "to": "USD", "amount": 1.0}
    )

    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert resp_json["amount"] == 1.0
    assert resp_json["convertedAmount"] == 0.91


def test_exchange_currency_rate_through_usd(
    app_client: TestClient, create_exc_rate_list: list[models.ExchangeRates]
) -> None:
    resp = app_client.get(
        "/exchange", params={"from": "EUR", "to": "GBP", "amount": 1.0}
    )

    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    # USD->EUR = 1.1, USD->GBP = 1.52, so EUR->GBP = 1.52 / 1.1
    assert resp_json["rate"] == 1.381818
    assert resp_json["amount"] == 1.0
    assert resp_json["convertedAmount"] == 1.38


def test_exchange_currency_rate_not_found(
    app_client: TestClient,
    create_currency_eur: models.Currency,
    create_currency_gpb: models.Currency,
) -> None:
    resp = app_client.get(
        "/exchange", params={"from": "EUR", "to": "GBP", "amount": 1.0}
    )

    resp_json = resp.json()

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp_json["message"] == "Exchange rate for currency pair not found"


def test_exchange_currency_not_found(
    app_client: TestClient,
    create_currency_eur: models.Currency,
    create_currency_gpb: models.Currency,
) -> None:
    resp = app_client.get(
        "/exchange", params={"from": "EUR", "to": "GBP", "amount": 1.0}
    )

    resp_json = resp.json()

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp_json["message"] == "Exchange rate for currency pair not found"


@pytest.mark.parametrize("amount", ["0", "-5", "abc", "NaN", "inf"])
def test_exchange_currency_invalid_amount(
    app_client: TestClient, create_exc_rate_usd_eur: models.ExchangeRates, amount: str
) -> None:
    resp = app_client.get(
        "/exchange", params={"from": "USD", "to": "EUR", "amount": amount}
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["message"].startswith("Invalid field 'amount'")


def test_exchange_currency_missing_amount(
    app_client: TestClient, create_exc_rate_usd_eur: models.ExchangeRates
) -> None:
    resp = app_client.get("/exchange", params={"from": "USD", "to": "EUR"})

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["message"] == "Missing required field 'amount'"


def test_exchange_currency_small_converted_amount(
    app_client: TestClient, create_exc_rate_usd_eur: models.ExchangeRates
) -> None:
    resp = app_client.get(
        "/exchange", params={"from": "USD", "to": "EUR", "amount": "0.001"}
    )

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["convertedAmount"] == 0.0


def test_exchange_currency_rounds_half_up(
    app_client: TestClient, create_exc_rate_usd_eur: models.ExchangeRates
) -> None:
    # 0.15 * 1.1 = 0.165 exactly: half-up gives 0.17, banker's rounding 0.16
    resp = app_client.get(
        "/exchange", params={"from": "USD", "to": "EUR", "amount": "0.15"}
    )

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["convertedAmount"] == 0.17


def test_exchange_currency_reversed_rate_rounds_to_nearest(
    app_client: TestClient,
    create_currency_usd: models.Currency,
    create_currency_eur: models.Currency,
) -> None:
    ExchangeRateFactory(
        base_currency=create_currency_usd, target_currency=create_currency_eur, rate=3
    )

    resp = app_client.get(
        "/exchange", params={"from": "EUR", "to": "USD", "amount": "3"}
    )

    # 1 / 3 = 0.3333333...: nearest is 0.333333, not rounded up to 0.333334
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["rate"] == 0.333333
    assert resp.json()["convertedAmount"] == 1.0


@pytest.mark.parametrize(
    "from_code, to_code",
    [("usd", "eur"), ("eur", "usd"), ("eur", "gbp")],
    ids=["direct", "reversed", "cross"],
)
def test_exchange_currency_case_insensitive(
    app_client: TestClient,
    create_exc_rate_list: list[models.ExchangeRates],
    from_code: str,
    to_code: str,
) -> None:
    resp = app_client.get(
        "/exchange", params={"from": from_code, "to": to_code, "amount": 10}
    )

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["baseCurrency"]["code"] == from_code.upper()
