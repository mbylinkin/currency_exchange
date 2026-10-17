from decimal import Decimal

from src.currency import service as currency_service
from src.exchange import exceptions, schemas
from src.exchange_rate import service as exchange_rate_service
from src.utils import round_amount, round_rate


def get_rate(from_currency: str, to_currency: str) -> Decimal:
    # Look for direct rate
    direct_rate = exchange_rate_service.get_exc_rate(f"{from_currency}{to_currency}")
    if direct_rate:
        return direct_rate.rate

    # Look for reversed rate
    reversed_rate = exchange_rate_service.get_exc_rate(f"{to_currency}{from_currency}")

    if reversed_rate:
        return round_rate(1 / reversed_rate.rate)

    # Cross rate: 1 FROM = 1 / (USD->FROM) USD = (USD->TO) / (USD->FROM) TO
    usd_from_pair = exchange_rate_service.get_exc_rate(f"USD{from_currency}")
    usd_to_pair = exchange_rate_service.get_exc_rate(f"USD{to_currency}")

    if usd_from_pair and usd_to_pair:
        return round_rate(usd_to_pair.rate / usd_from_pair.rate)

    raise exceptions.CurrencyPairExcRateNotFound()


def exc_currency(
    from_currency: str, to_currency: str, amount: Decimal
) -> schemas.Exchange:
    from_currency_value = currency_service.get_valid_currency(from_currency)
    to_currency_value = currency_service.get_valid_currency(to_currency)
    rate = get_rate(from_currency, to_currency)

    exchange = schemas.Exchange(
        base_currency=from_currency_value,
        target_currency=to_currency_value,
        rate=rate,
        amount=amount,
        converted_amount=round_amount(amount * rate),
    )
    return exchange
