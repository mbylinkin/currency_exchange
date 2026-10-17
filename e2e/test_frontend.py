import httpx
import pytest
from playwright.sync_api import Page, expect

# Known spec violations. strict=True fails the run once a bug is fixed,
# so the fix must also remove its marker.
BUG_DUPLICATE_RATE_MESSAGE = pytest.mark.xfail(
    strict=True, reason="duplicate exchange rate returns 409 with 'Server error'"
)
BUG_CROSS_RATE = pytest.mark.xfail(
    strict=True, reason="cross rate via USD is inverted: (USD->A) / (USD->B)"
)


def seed_currency(api: httpx.Client, code: str, name: str, sign: str) -> None:
    resp = api.post("/currencies", data={"code": code, "name": name, "sign": sign})
    resp.raise_for_status()


def seed_rate(api: httpx.Client, base: str, target: str, rate: str) -> None:
    resp = api.post(
        "/exchangeRates",
        data={"baseCurrencyCode": base, "targetCurrencyCode": target, "rate": rate},
    )
    resp.raise_for_status()


@pytest.fixture()
def usd_eur_gbp(api: httpx.Client) -> None:
    seed_currency(api, "USD", "US Dollar", "$")
    seed_currency(api, "EUR", "Euro", "€")
    seed_currency(api, "GBP", "Pound Sterling", "£")
    seed_rate(api, "USD", "EUR", "0.95")
    seed_rate(api, "USD", "GBP", "0.8")


def error_toast(page: Page):
    return page.locator("#api-error-toast .toast-body")


def test_page_shows_currencies_and_rates(
    page: Page, frontend: str, usd_eur_gbp: None, page_errors: list[str]
) -> None:
    page.goto(frontend)

    currencies = page.locator(".currencies-table tbody tr")
    expect(currencies).to_have_count(3)
    expect(currencies.nth(1)).to_contain_text("EUR")
    expect(currencies.nth(1)).to_contain_text("Euro")
    expect(currencies.nth(1)).to_contain_text("€")

    rates = page.locator(".exchange-rates-table tbody tr")
    expect(rates).to_have_count(2)
    expect(rates.nth(0)).to_contain_text("USDEUR")
    expect(rates.nth(0)).to_contain_text("0.95")
    assert page_errors == []


def test_add_currency(page: Page, frontend: str, api: httpx.Client) -> None:
    page.goto(frontend)

    page.fill("#add-currency-code", "JPY")
    page.fill("#add-currency-name", "Yen")
    page.fill("#add-currency-sign", "¥")
    page.click("text=Add Currency")

    expect(page.locator(".currencies-table tbody tr")).to_contain_text(["JPY"])
    assert [c["code"] for c in api.get("/currencies").json()] == ["JPY"]


def test_add_duplicate_currency_shows_error(
    page: Page, frontend: str, usd_eur_gbp: None
) -> None:
    page.goto(frontend)

    page.fill("#add-currency-code", "USD")
    page.fill("#add-currency-name", "US Dollar")
    page.fill("#add-currency-sign", "$")
    page.click("text=Add Currency")

    expect(error_toast(page)).to_contain_text("already exists")


def test_add_currency_missing_field_shows_error(page: Page, frontend: str) -> None:
    page.goto(frontend)

    page.fill("#add-currency-code", "JPY")
    page.fill("#add-currency-name", "Yen")
    page.click("text=Add Currency")

    expect(error_toast(page)).to_contain_text("sign")


def test_add_exchange_rate(
    page: Page, frontend: str, api: httpx.Client, usd_eur_gbp: None
) -> None:
    page.goto(frontend)

    page.select_option("#new-rate-base-currency", "EUR")
    page.select_option("#new-rate-target-currency", "GBP")
    page.fill("#exchange-rate", "0.85")
    page.click("text=Add Exchange Rate")

    expect(page.locator(".exchange-rates-table tbody tr")).to_have_count(3)
    assert api.get("/exchangeRate/EURGBP").json()["rate"] == 0.85


@BUG_DUPLICATE_RATE_MESSAGE
def test_add_duplicate_exchange_rate_shows_error(
    page: Page, frontend: str, usd_eur_gbp: None
) -> None:
    page.goto(frontend)

    page.select_option("#new-rate-base-currency", "USD")
    page.select_option("#new-rate-target-currency", "EUR")
    page.fill("#exchange-rate", "1")
    page.click("text=Add Exchange Rate")

    expect(error_toast(page)).to_contain_text("already exists")


def test_edit_exchange_rate(
    page: Page, frontend: str, api: httpx.Client, usd_eur_gbp: None
) -> None:
    page.goto(frontend)

    row = page.locator(".exchange-rates-table tbody tr", has_text="USDEUR")
    row.locator("text=Edit").click()
    page.fill("#exchange-rate-input", "0.97")
    page.click("text=Save changes")

    expect(row).to_contain_text("0.97")
    assert api.get("/exchangeRate/USDEUR").json()["rate"] == 0.97


@pytest.mark.parametrize(
    ("base", "target", "amount", "converted"),
    [
        pytest.param("USD", "EUR", "10", "9.5", id="direct"),
        pytest.param("EUR", "USD", "10", "10.53", id="reversed"),
        # USD->EUR = 0.95, USD->GBP = 0.8, so EUR->GBP = 0.8 / 0.95
        pytest.param(
            "EUR", "GBP", "10", "8.42", id="cross-via-usd", marks=BUG_CROSS_RATE
        ),
    ],
)
def test_convert(
    page: Page,
    frontend: str,
    usd_eur_gbp: None,
    base: str,
    target: str,
    amount: str,
    converted: str,
) -> None:
    page.goto(frontend)

    page.select_option("#convert-base-currency", base)
    page.select_option("#convert-target-currency", target)
    page.fill("#convert-amount", amount)
    page.click("button:text('Convert')")

    expect(page.locator("#convert-converted-amount")).to_have_value(converted)


def test_convert_without_rate_shows_error(
    page: Page, frontend: str, api: httpx.Client
) -> None:
    seed_currency(api, "EUR", "Euro", "€")
    seed_currency(api, "GBP", "Pound Sterling", "£")
    page.goto(frontend)

    page.select_option("#convert-base-currency", "EUR")
    page.select_option("#convert-target-currency", "GBP")
    page.fill("#convert-amount", "10")
    page.click("button:text('Convert')")

    expect(error_toast(page)).to_contain_text("not found")


def test_convert_invalid_amount_shows_error(
    page: Page, frontend: str, usd_eur_gbp: None
) -> None:
    page.goto(frontend)

    page.select_option("#convert-base-currency", "USD")
    page.select_option("#convert-target-currency", "EUR")
    page.fill("#convert-amount", "-5")
    page.click("button:text('Convert')")

    expect(error_toast(page)).to_contain_text("amount")
