from fastapi.testclient import TestClient

from fastapi import status

from src.models import Currency


def test_add_currency(app_client: TestClient) -> None:
    expected = {
        "id": 1,
        "code": "USD",
        "name": "US Dollar",
        "sign": "$",
    }
    resp = app_client.post(
        "/currencies/",
        data={
            "code": "USD",
            "name": "US Dollar",
            "sign": "$",
        },
    )
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp_json == expected


def test_add_currency_already_exists(
    app_client: TestClient, create_currency_usd: Currency
) -> None:
    resp = app_client.post(
        "/currencies/",
        data={
            "code": "USD",
            "name": "US Dollar",
            "sign": "$",
        },
    )
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_409_CONFLICT
    assert resp_json["detail"] == "Currency with this code already exists"


def test_get_currency_empty_code(app_client: TestClient) -> None:
    resp = app_client.get("/currency/")
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp_json["detail"] == "Currency code is required"


def test_get_currency_by_code(
    app_client: TestClient, create_currency_eur: Currency
) -> None:
    expected = {
        "id": create_currency_eur.id,
        "code": create_currency_eur.code,
        "name": create_currency_eur.name,
        "sign": create_currency_eur.sign,
    }

    resp = app_client.get(f"/currency/{create_currency_eur.code}")
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert resp_json["code"] == expected["code"]
    assert resp_json["name"] == expected["name"]
    assert resp_json["sign"] == expected["sign"]


def test_get_currency_by_code_not_found(app_client: TestClient) -> None:
    resp = app_client.get("/currency/USD")
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp_json["detail"] == "Currency not found"


def test_get_currencies(app_client: TestClient, create_currency_eur: Currency) -> None:
    expected = [
        {
            "id": create_currency_eur.id,
            "code": create_currency_eur.code,
            "name": create_currency_eur.name,
            "sign": create_currency_eur.sign,
        },
    ]
    resp = app_client.get("/currencies/")
    resp_json = resp.json()

    assert resp.status_code == status.HTTP_200_OK
    assert resp_json == expected
