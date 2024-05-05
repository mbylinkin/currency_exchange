from fastapi.testclient import TestClient
from fastapi import status

from src import models


def test_add_exchange_rate(
    app_client: TestClient,
    create_currency_usd: models.Currency,
    create_currency_eur: models.Currency,
) -> None:
    expected = {
        "id": 1,
        "rate": 1.98,
        "baseCurrency": {
            "code": create_currency_usd.code,
            "id": create_currency_usd.id,
            "name": create_currency_usd.name,
            "sign": create_currency_usd.sign,
        },
        "targetCurrency": {
            "code": create_currency_eur.code,
            "id": create_currency_eur.id,
            "name": create_currency_eur.name,
            "sign": create_currency_eur.sign,
        },
    }
    resp = app_client.post(
        "/exchangeRates/",
        data={
            "baseCurrencyCode": create_currency_usd.code,
            "targetCurrencyCode": create_currency_eur.code,
            "rate": 1.98,
        },
    )
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp_json == expected


def test_get_exchange_rate_list(
    app_client: TestClient, create_exc_rate_usd_eur: models.ExchangeRates
) -> None:
    expected = [
        {
            "id": create_exc_rate_usd_eur.id,
            "rate": float(create_exc_rate_usd_eur.rate),
            "baseCurrency": {
                "code": create_exc_rate_usd_eur.base_currency.code,
                "id": create_exc_rate_usd_eur.base_currency.id,
                "name": create_exc_rate_usd_eur.base_currency.name,
                "sign": create_exc_rate_usd_eur.base_currency.sign,
            },
            "targetCurrency": {
                "code": create_exc_rate_usd_eur.target_currency.code,
                "id": create_exc_rate_usd_eur.target_currency.id,
                "name": create_exc_rate_usd_eur.target_currency.name,
                "sign": create_exc_rate_usd_eur.target_currency.sign,
            },
        }
    ]

    resp = app_client.get("/exchangeRates/")
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp_json) == len(expected)
    assert resp_json[0]["rate"] == expected[0]["rate"]
    assert resp_json[0]["baseCurrency"] == expected[0]["baseCurrency"]
    assert resp_json[0]["targetCurrency"] == expected[0]["targetCurrency"]


def test_get_exchange_rate_by_code(
    app_client: TestClient, create_exc_rate_usd_eur: models.ExchangeRates
) -> None:
    expected = {
        "id": create_exc_rate_usd_eur.id,
        "rate": float(create_exc_rate_usd_eur.rate),
        "baseCurrency": {
            "code": create_exc_rate_usd_eur.base_currency.code,
            "id": create_exc_rate_usd_eur.base_currency.id,
            "name": create_exc_rate_usd_eur.base_currency.name,
            "sign": create_exc_rate_usd_eur.base_currency.sign,
        },
        "targetCurrency": {
            "code": create_exc_rate_usd_eur.target_currency.code,
            "id": create_exc_rate_usd_eur.target_currency.id,
            "name": create_exc_rate_usd_eur.target_currency.name,
            "sign": create_exc_rate_usd_eur.target_currency.sign,
        },
    }

    resp = app_client.get("/exchangeRate/USDEUR")
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert resp_json["rate"] == expected["rate"]
    assert resp_json["baseCurrency"] == expected["baseCurrency"]
    assert resp_json["targetCurrency"] == expected["targetCurrency"]


def test_get_exchange_rate_by_code_not_found(
    app_client: TestClient, create_exc_rate_usd_eur: models.ExchangeRates
) -> None:
    resp = app_client.get("/exchangeRate/USDGBP")
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp_json["detail"] == "Exchange rate not found"


def test_get_exchange_rate_empty_code(app_client: TestClient) -> None:
    resp = app_client.get("/exchangeRate/")
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp_json["detail"] == "Exchange rate code is required"


def test_update_exchange_rate(
    app_client: TestClient, create_exc_rate_usd_eur: models.ExchangeRates
) -> None:
    new_rate = 1.5
    expected = {
        "id": create_exc_rate_usd_eur.id,
        "rate": new_rate,
        "baseCurrency": {
            "code": create_exc_rate_usd_eur.base_currency.code,
            "id": create_exc_rate_usd_eur.base_currency.id,
            "name": create_exc_rate_usd_eur.base_currency.name,
            "sign": create_exc_rate_usd_eur.base_currency.sign,
        },
        "targetCurrency": {
            "code": create_exc_rate_usd_eur.target_currency.code,
            "id": create_exc_rate_usd_eur.target_currency.id,
            "name": create_exc_rate_usd_eur.target_currency.name,
            "sign": create_exc_rate_usd_eur.target_currency.sign,
        },
    }

    resp = app_client.patch("/exchangeRate/USDEUR", data={"rate": new_rate})
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert resp_json["rate"] == expected["rate"]
    assert resp_json["baseCurrency"] == expected["baseCurrency"]
    assert resp_json["targetCurrency"] == expected["targetCurrency"]
