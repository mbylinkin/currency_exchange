import decimal

from src import constants
from src.exchange import schemas

from src.currency import service as currency_service
from src.exchange_rate import service as exchange_rate_service

from src.exchange import exceptions
from src.utils import round_up


def get_rate(from_currency: str, to_currency: str):
    # Look for direct rate
    direct_rate = exchange_rate_service.get_exc_rate(f"{from_currency}{to_currency}")
    if direct_rate:
        return direct_rate.rate

    # Look for reversed rate
    reversed_rate = exchange_rate_service.get_exc_rate(f"{to_currency}{from_currency}")

    if reversed_rate:
        return round_up(1 / reversed_rate.rate, constants.EXCH_RATE_ACCURACY)

    usd_from_pair = exchange_rate_service.get_exc_rate(f"USD{from_currency}")
    usd_to_pair = exchange_rate_service.get_exc_rate(f"USD{to_currency}")

    if usd_from_pair and usd_to_pair:
        return round_up(
            usd_from_pair.rate / usd_to_pair.rate, constants.EXCH_RATE_ACCURACY
        )

    raise exceptions.CurrencyPairExcRateNotFound()


def exc_currency(
    from_currency: str, to_currency: str, amount: float
) -> schemas.Exchange:
    from_currency_value = currency_service.get_valid_currency(from_currency)
    to_currency_value = currency_service.get_valid_currency(to_currency)
    rate = get_rate(from_currency, to_currency)

    exchange = schemas.Exchange(
        base_currency=from_currency_value,
        target_currency=to_currency_value,
        rate=rate,
        amount=amount,
        converted_amount=round(decimal.Decimal(amount) * decimal.Decimal(rate), 2),
    )
    return exchange
